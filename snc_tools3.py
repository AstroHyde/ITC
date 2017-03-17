import numpy
from pylab import *
import scipy
from scipy.signal import cspline1d, cspline1d_eval
from scipy import interpolate
from scipy.constants import constants
from scipy import special





class FluxTools:
    
    def __init__(self,**kw):
        self.template=self.LoadFile(kw["template"])
        self.filter=self.LoadFile(kw["filter"])
        self.magnitude=kw["magnitude"]

    def LoadFile(self,infile,col0=0,col1=1):
        #this exist because back compatibility with my older code
        
        try:
            data=numpy.genfromtxt(infile)
            c1,c2=data[:,col0],data[:,col1]
        
        except:
            print ("error in loading file % s" % (infile))
        
        return numpy.asarray((c1,c2))
            
    
    
    
    
    def PassBandFLux(self,sed,band,debug=0):
            """
            Calculate the flux in a given passpand
            
            """
            l_sed=sed[0,:] # sed wavelenght range
            f_sed=sed[1,:] # sed flux density erg cm^-2 s^-1 Ang^-1
            l_band=band[0,:] # filter wavelenght range
            f_band=band[1,:] # filter transmission

            #interpolate the filter response curve
            tck_band=interpolate.splrep(l_band,f_band,s=0,k=3)
            #find the portion  of the sed covered by the filter 
            mask=[(l_sed>=l_band.min()) & (l_sed<=l_band.max())]
            
            new_l_band=l_sed[mask]
            
            new_f_band=interpolate.splev(new_l_band,tck_band,der=0)
            
            if debug:
                        plot(l_sed,f_sed,"k-")
                        plot(l_band,f_band,"ro",new_l_band,new_f_band,"b-")
                        plot(new_l_band,f_sed[mask]*new_f_band,"g-")
            
            integrated_flux=numpy.trapz(f_sed[mask]*new_f_band*new_l_band,new_l_band)/numpy.trapz(new_f_band*new_l_band,new_l_band)
            
            return integrated_flux
    
    def GetLambdaEff(self):
            lef=numpy.trapz(self.filter[0,:]*self.filter[1,:]) / numpy.trapz(self.filter[1,:]/self.filter[0,:])
            lef=numpy.sqrt(lef)
            return leff
    
    def MagToFluxedSed(self,mag):
            
            sed=self.template
            filter=self.filter
            
            bandflux=self.PassBandFLux(sed,filter,debug=0)
            
            
            zpt_sed=numpy.array((sed[0,:],3631*2.99792458E-05/(sed[0,:])**2)) # Jansky to erg/cm^2/s/ang
            abzeropoint=self.PassBandFLux(zpt_sed,filter,debug=0)
            fnorm=abzeropoint*10**(-0.4*mag)/bandflux
            normsed=numpy.array((sed[0,:],sed[1,:]*fnorm))
            
            return normsed
    
    def SedToMag(self,const=10**(-16)):
        """
        Return  the magnitude in the given passband 
        """
        
        sed=numpy.copy(self.template)
        sed[1,:]=sed[1,:]*const
        
        filter=self.filter
        
        bandflux=self.PassBandFLux(sed,filter,debug=0)
            
        #zeropoint=filter_zeropoint *2.99792458E-05/leff**2
        # [Y erg/cm^2/s/A]             = 2.99792458E-05 * [X1 Jy] / [X2 A]^2

        ab_sed=numpy.array((sed[0,:],2.99792458E-05 * (3631.) / (sed[0,:]**2)))
        
        zero_ab_sed=self.PassBandFLux(ab_sed,filter)
        mag=-2.5*numpy.log10((bandflux/zero_ab_sed))
        return mag
        
        
   
    def plot2darr(self,arr,lsty="k-"):
        
        gca().plot(arr[0,:],arr[1,:],lsty)
        
    def GetFlux(self):
        return self.PassBandFLux(self.template,self.filter,debug=0)
    
    def ToABmag(self,mag):
        """
        Scale the sed to a broadband magnitude and return it in AB
        """
        fluxed=self.MagToFluxedSed(mag) # wavelength vs flux density scaled to provided mangnitudde
        ab_mag=-2.5*numpy.log10(fluxed[1,:])-2.402-5.*numpy.log10(fluxed[0,:]) # transform to AB mag
        out=numpy.zeros((ab_mag.shape[0],2))
        out[:,1]=ab_mag
        out[:,0]=fluxed[0,:]
        return out
    
class SignalTools:
    
    def __init__(self,**kw):
        self.object=kw["object"]# spectrum of the object in ab magnitude
        #self.magnitude=kw["mag"]
        self.airmass=kw["airmass"]
        self.exptime=kw["exptime"]
        self.fwhm=kw["fwhm"] # fwhm in the spatial direction
        self.slit=kw["slit"]
        self.extinction=kw["extinction_curve"]
        self.sensitivity=kw["sens_func"] #sensitivity func the ab mag which give 1 count/s/Ang
        
       
        
    def InterpolateSpectrum(self,spectrum,reference):
        """Interpolate a spectrum to have the same sampling of the reference
        
        """
        tck=interpolate.splrep(spectrum[:,0],spectrum[:,1],s=0,k=1)
        wav_ref=reference[:,0]
        wav_spectrum=spectrum[:,0]
        
        mask=(wav_ref>=wav_spectrum.min()) & (wav_ref<=wav_spectrum.max())
        
        new_wav_ref=wav_ref[mask]
        new_reference=reference[:,1][mask]
        new_spectrum=interpolate.splev(new_wav_ref,tck,der=0)
        out=zeros((new_wav_ref.shape[0],3))  
        out[:,0]=new_wav_ref
        out[:,1]=new_spectrum
        out[:,2]=new_reference
    
        return out
      
    
    def GetCounts(self):
        """
        Compute the counts per Angstrom 
        """
        sens_obj_array=self.InterpolateSpectrum(self.sensitivity,self.object)
        #print (self.sensitivity.shape,sens_obj_array.shape)
        dmag=numpy.zeros((sens_obj_array.shape[0],2))
        dmag[:,0]=sens_obj_array[:,0]
        dmag[:,1]=sens_obj_array[:,2]-sens_obj_array[:,1] # object - sensitivity
        #print (dmag.shape,self.extinction.shape)
         
    
        #interpolate extinction curve
        interp_extinct=self.InterpolateSpectrum(self.extinction,dmag)
        
        dexticnt=interp_extinct[:,1]*(self.airmass-1)
        
        #wav_arr=sens_obj_arr[:,0]
        #
        countspera=10**(-0.4*(dmag[:,1]+dexticnt))*self.exptime
        out=numpy.zeros((countspera.shape[0],2))
        out[:,0]=interp_extinct[:,0]
        out[:,1]=countspera
        return out
    def slit_tran(self):
        swidth=self.slit
        seeing=self.fwhm
    
    #tran=special.erf((swidth/seeing)*math.log(math.sqrt(2)))
        tran=special.erf((swidth/2)/(math.sqrt(2)*seeing/2.35482))
        return tran


if (__name__=="__main__"):
    #obj=numpy.genfromtxt("eGalaxy_ang.dat")[:,0:2]
    ft=FluxTools(template="data/eGalaxy_ang.dat",filter="data/filterV_ang.dat",magnitude=19.)
    ab_mag=ft.ToABmag(17.)
    obj=ab_mag
    sens=numpy.genfromtxt("data/Grism300R_sky.dat")[:,0:2]
    ctio=numpy.genfromtxt("data/ctioextinct.dat")
    counts=SignalTools(object=obj,sens_func=sens,exptime=120.,airmass=1.5,mag=1.,slit=1.,extinction_curve=ctio,fwhm=1.,seeing=1)
    counts_spectrum= counts.GetCounts()
    slit_loss=counts.slit_tran()
    print ("slit losses",counts.fwhm,counts.slit,slit_loss)
    fig=plot(counts_spectrum[:,0],counts_spectrum[:,1])
    sky=FluxTools(template="data/UVES_sky.txt",filter="data/filterV_ang.dat",magnitude=21.8)
    sky_ab=sky.ToABmag(21.8)
    counts.object=sky_ab
    counts.airmass=1.
    sky_counts=counts.GetCounts()
    
    plot(sky_counts[:,0],sky_counts[:,1])
    
    
    
    show()
    #savefig(sys.stdout,format="png")
