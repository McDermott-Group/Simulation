"""
Chris Wilen
McDermott Group, UW Madison

This file provides objects for a variety of different types of cpw resonators.
"""

from scipy.constants import c, epsilon_0, mu_0, h, hbar, e, pi
from scipy.special import ellipk, ellipkm1
import numpy as np
import capacitance as cap

def dBm_to_watts(dB):
    return 10**(dB/10.) * 0.001

def watts_to_dBm(watts):
    return np.log10( 1000 * watts ) * 10

class CPW(object):
    """
    w = width of center trace [um]
    s = width of gap [um]
    t = thickness [um]
    h = height of substrate [um]
    l = length of CPW [um]
    e1 = relative permitivity of substrate
    material = ['nb','al'], assigns Tc and rho
    tand =
    physics from gupta, goppl unless otherwise noted.
    """
    def __init__(self, w=10., s=6., t=.1, h=480., e1=11.8, material="nb", tand=.15e-6):
        self.w = w*1e-6
        self.s = s*1e-6
        self.t = t*1e-6
        self.h = h*1e-6
        self.e0 = 1.  # air above CPW
        self.e1 = e1  # dielectric
        self.tand = tand
        self.material = material
        self.kineticInductanceCorrectionOn = True
        self.metalThicknessCorrectionOn = True

#     Turn on/off corrections due to metal thickness, kinetic inductance
    def setMetalThicknessCorrection(self, on):
        self.metalThicknessCorrectionOn = on

    def setKineticInductanceCorrection(self, on):
        self.kineticInductanceCorrectionOn = on

#     Effective Dielectric Constant from Silicon-Air Interface
    def _Delta(self):
        """correction for thickness of metal"""
        return (1.25*self.t/pi)*( 1 + np.log(4*pi*self.w/self.t) )

    def _s_eff(self):
        if self.metalThicknessCorrectionOn:
            return self.s - self._Delta()
        else:
            return self.s
            
    def _w_eff(self):
        if self.metalThicknessCorrectionOn:
            return self.w + self._Delta()
        else:
            return self.w

    def _k0(self):
        return self._w_eff()/(self._w_eff()+2*self._s_eff())

    def _kp0(self):
        return np.sqrt(1-self._k0()**2)

    def _k1(self):
        return np.sinh(pi*self._w_eff()/(4*self.h))/np.sinh(pi*(2*self._s_eff()+self._w_eff())/(4*self.h))

    def _kp1(self):
        return np.sqrt(1-self._k1()**2)
    
    def _C1(self):
        """Capacitance of the top plane of a cpw.  (Gupta)"""
        return 2*epsilon_0*ellipk(self._k0()**2)/ellipk(self._kp0()**2)
    
    def _C2(self):
        """Capacitance of the bottom plane of a cpw.  (Gupta)"""
        return 2*epsilon_0*(self.e1-1)*ellipk(self._k1()**2)/ellipk(self._kp1()**2)

    def Eeff(self):
        """Effective (relative) dielectric constant"""
        return (2*self._C1()+self._C2())/2/self._C1()

#     Kinetic Inductance Calculation
#     from Clem, "Inductances and attenuation constant for a thin-film SC CPW res"

    def _g(self, k, eps):
        return 1./( 2*(1-k)*ellipk(k**2)**2 ) * np.log( 2*(1-k)/eps/(1+k) )

    def _q(self, u):
        return (np.sinh(u) + u)/8/np.sinh(u/2)**2

    def Llk(self):
        """Kinetic inductance per unit length."""
        if self.material.lower() == "al":
            self.Tc = 1.23
            self.rho = 4e-9
        elif self.material.lower() == 'nb':
            self.Tc = 8
            self.rho = 4e-9
        l0 = 1.05e-3*np.sqrt(self.rho/self.Tc)
        return mu_0*l0/self.w*self._q(self.t/l0)*self._g( (self.w/2)/(self.w/2+self.s), 1 )

#     Circuit Parameters

    def Llg(self):
        """Geometric inductance per unit length."""
        return mu_0*ellipk(self._kp0()**2)/(4*ellipk(self._k0()**2))

    def Ll(self):
        """Total Inductance per unit length.  Kinetic inductance corrections can
           be turned on or off."""
        if self.kineticInductanceCorrectionOn:
            return self.Llg() + self.Llk()
        else:
            return self.Llg()

    def Cl(self):
        """Capacitance per unit length"""
        return 4*epsilon_0*self.Eeff()*ellipk(self._k0()**2)/ellipk(self._kp0()**2)

    def Gl(self, w):
        return w * self.tand * self._C2()

    def vph(self):
        """Phase velocity."""
        return 1./np.sqrt(self.Ll()*self.Cl())

    def z0(self):
        """Characteristic Impedance."""
        return np.sqrt(self.Ll()/self.Cl())

#     Loss
#     from Pozar p.50

    def gamma(self, w):
        return np.sqrt( 1j*w*self.Ll()*( self.Gl(w) + 1j*w*self.Cl() ) )

    def alpha(self, w):
        return self.gamma(w).real

    def beta(self, w):
        return self.gamma(w).imag

#      String

    def __str__(self):
        return "Cl = {} pF/um\nLl = {} nH/um\nvph = {}e8 m/s\nz0 = {} Ohms".format( self.Cl()*1e12/1e6, self.Ll()*1e9/1e6, self.vph()/1e8, self.z0())


class CPWWithBridges(CPW):
    def __init__(self, bridgeSpacing = 100, bridgeWidth = 2, oxideLossTan = 3e-3, t_oxide = 0.1, e_oxide = 3.9, **kwargs):
        self.bridgeSpacing = bridgeSpacing
        self.bridgeWidth = bridgeWidth
        self.oxideLossTan = oxideLossTan
        self.t_oxide = t_oxide
        self.e_oxide = e_oxide
        super(CPWWithBridges,self).__init__(**kwargs)
    
    def Cl_bridge_air(self):
        """Capacitance per unit length of bridge through the air."""
        bridgeCap = cap.OverlapCapacitor(self.bridgeWidth*1e6*self.w, t = self.t_oxide, eps_r = self.e0)
        return 1e6*bridgeCap.cap()/self.bridgeSpacing
    
    def Cl_bridge_dielectric(self):
        """Capacitance per unit length of bridge through the air."""
        bridgeCap = cap.OverlapCapacitor(self.bridgeWidth*1e6*self.w, t = self.t_oxide, eps_r = self.e_oxide)
        return 1e6*bridgeCap.cap()/self.bridgeSpacing
    
    def EeffForPlainCPW(self):
        return super(CPWWithBridges,self).Eeff()
    
    def Eeff(self):
        """Effective (relative) permetivity with bridges included."""
        return (2*self._C1()+self._C2()+self.Cl_bridge_dielectric())/(2*self._C1()+self.Cl_bridge_air())

    def Cl(self):
        """Note that this does not take into account the magnitude of the E-field,
        which changes along a standing wave."""
        # multiplied factor below removes changes in Eeff for capacitance, since
        # it is really the additional capacitance that changes the Eeff, not the
        # other way around.
        cpwCap = super(CPWWithBridges,self).Cl() * self.EeffForPlainCPW()/self.Eeff()
        return cpwCap + self.Cl_bridge_dielectric()
    
    def Llg(self):
        return self.Eeff()/c**2/self.Cl()
    
    def Gl_bridge(self, w):
        return w * self.oxideLossTan * self.Cl_bridge_dielectric()
    
    def Gl(self, w):
        return super(CPWWithBridges,self).Gl(w) + self.Gl_bridge(w)


class Resonator(object):
    """Base for any resonator to inherit from.  Defaults to lambda/2"""
    def __init__(self, cpw, l):
        self.l = l*1e-6
        self.cpw = cpw
        self.wavelengthFraction = 2 # lambda/2 or lambda/4
        self.couplings_C = {}
        self.couplings_L = {}

    def f0(self):
        # return c/(np.sqrt(self.cpw.Eeff())*2*self.l) # Goppl for L/2, doesn't include kinetic inductance?
        return self.cpw.vph()/(self.l*self.wavelengthFraction)

    def w0(self):
        return 2*pi*self.f0() # Goppl

    #     Circuit Parameters with Loss
    
    def setLengthFromFreq(self, f):
        self.l = self.cpw.vph()/f/self.wavelengthFraction
        return self.l

    def L(self):
        # return 2*self.cpw.Ll()*self.l/(pi**2) # Goppl
        return 1./self.C()/self.w0()**2 # Pozar p.283

    def C(self):
        # these are equiv. (I checked)
        # return self.cpw.Cl()*self.l/2 # Goppl
        return np.pi/self.wavelengthFraction/self.w0()/self.cpw.z0() # Pozar p.283

    def R(self):
        return self.cpw.z0()/(self.cpw.alpha(self.w0())*self.l) # Pozar p.283, Goppl

    def Qint(self):
        return self.R()*np.sqrt(self.C()/self.L()) # Goppl, Pozar p.283, all are equiv.
        # return self.w0()*self.R()*self.C()
        # return np.pi/2/cpw.alpha(self.w0())/self.l
        # return cpw.beta(self.w0())/2/cpw.alpha(self.w0())

    def wn(self):
        return 1./np.sqrt(self.L()*self.C()) # Goppl
        # return self.Qint()/(self.R()*self.C())
    
    def fn(self):
        return self.wn()/2/pi

    #   Loading
    
    def extraRFromCouplingC(self, name, Z0=50.):
        '''Effective input resistance to ground'''
        c = self.couplings_C[name]
        return (1. + (self.wn()*c*Z0)**2)/(self.wn()*c)**2/Z0 # Goppl
        # return Z0*(1+self.Qs(Z0, self.cki)**2) # Ted's notes
    
    def extraCFromCouplingC(self, name, Z0=50.):
        '''Effective input capacitance to ground'''
        c = self.couplings_C[name]
        return c/(1. + (self.wn()*c*Z0)**2)
    
    def addCapacitiveCoupling(self, name, c):
        self.couplings_C[name] = c

    def wl(self):
        '''Loaded frequency in rad/s'''
        extraCs = [self.extraCFromCouplingC(name) for name in self.couplings_C.keys()]
        return 1./np.sqrt(self.L()*(self.C() + sum(extraCs)))

    def fl(self):
        '''Loaded frequency'''
        return self.wl()/2/pi
    
    def Qc(self, name=None):
        if name is None:
            '''Total coupling Q'''
            names = self.couplings_C.keys() + list(set(self.couplings_L) - set(self.couplings_C))
            q = [1./self.Qc(name) for name in names]
            return 1./(1./self.Qint() + sum(q))
        else:
            '''Coupling Q for a specific coupling'''
            extraR = self.extraRFromCouplingC(name)
            # extraR = extraRFromCouplingL(name)
            if name in self.couplings_C:
                extraC = self.extraCFromCouplingC(name)
            else:
                extraC = 0
            # if name in self.couplings_L:
            #     extraL = extraLFromCouplingL(name)
            # else:
            #     extraL = 0
            extraL = np.inf
            # return self.wn() * (self.C() + self.Cout())/(1./self.R() + 1./self.Rout())
            return 1./(1./self.R() + 1./extraR) * np.sqrt( (self.C() + extraC) * (1./self.L() + 1./extraL) )

    def Ql(self):
        '''Loaded Q, including internal loss.'''
        names = self.couplings_C.keys() + list(set(self.couplings_L) - set(self.couplings_C))
        r = []
        c = []
        l = []
        for name in names:
            if name in self.couplings_C:
                c.append( self.extraCFromCouplingC( name ) )
                r.append( self.extraRFromCouplingC( name ) )
            if name in self.couplings_L:
                l.append( self.extraLFromCouplingL( name ) )
                r.append( self.extraRFromCouplingL( name ) )
        return 1./(1./self.R() + sum([1./x for x in r])) * np.sqrt(self.C() + sum(c)) * np.sqrt(1./self.L() + sum([1./x for x in l]))
        # return 1./(1./self.Qint() + 1./self.Qin() + 1./self.Qout()) # does the just account for C() twice?  Goppl says only works at w=w*

    def kappa(self):
        '''Photon loss rate'''
        return self.wl()/self.Ql()
    
    def kappa(self, name):
        return self.wl()/self.Qc(name)

    def photons(self, Pin):
        '''Number of photons in the steady state cavity, based on input power [dBm]'''
        # From Matt Beck's notes on the wiki
        return dBm_to_watts(Pin) * self.Ql()**2 / self.Qc() / hbar / self.wl()**2

    def __str__(self):
        #return "l = {} um\nf = {} GHz\nQ = {}\nk = {} MHz".format(self.cpw.l*1e6,self.fl(), self.Ql(), self.kappa()/2e6/pi)
        return "l = {} um\nf = {} GHz\nQ = {}\nk = {} MHz\nC = {} pF\nL = {} nH\nR = {} Ohms".format(self.l*1e6, self.fl()/1e9, self.Ql(), self.kappa()/2e6/pi, self.C()*1e12, self.L()*1e9, self.R() )


class HalfLResonator(Resonator):
    """Open-circuited Lambda/2 resonator"""
    def __init__(self, *args, **kwargs):
        super(HalfLResonator,self).__init__(*args)
        self.wavelengthFraction = 2
        for name in kwargs.keys():
            self.addCapacitiveCoupling(name,kwarg[name])


class QuarterLResonator(Resonator):
    """Open-circuited Lambda/2 resonator"""
    def __init__(self, *args, **kwargs):
        super(QuarterLResonator,self).__init__(*args)
        self.wavelengthFraction = 4