#!/usr/bin/env python
import sys, subprocess, os
import numpy as np
from scipy import *
import copy, Fileio, re
from scipy import interpolate
import shutil
import glob
from INPUT import *
import argparse
from argparse import RawTextHelpFormatter
import Struct

#import matplotlib
#matplotlib.use('ps')
from matplotlib.font_manager import fontManager, FontProperties
import matplotlib.pyplot as plt
from pylab import *
import scipy.interpolate
import re

class PostProcess:
	"""DMFTwDFT PostProcess

	This class contains methods to perform post processing of the DMFT calculations. 


	"""

	def __init__(self):
		"""
		Initializes the following:
		"""

		#mpirun
		if os.path.exists("para_com.dat"):
			fipa=open('para_com.dat','r')
			self.para_com=str(fipa.readline())[:-1]
			fipa.close()
		else:
			self.para_com=""


		#dmft_bin
		self.path_bin=p['path_bin']


	def checksig(self):	
   		"""
   		Checks if Sig.out is created in the ac directory.
   		"""

		if os.path.exists("./ac/Sig.out"):
			return True 
		else:
			print('Analytic Continuation incomplete. Sig.out not found.')
			return False

	def interpol(self,emin,emax,rom,broaden,dest_dir):
		"""
		This performs the interpolation of points on the real axis.
		It also creates SigMdc.out and SigMdc_dn.out required for old version
		of bandplotting.
		"""
		print('\nInterpolating points on real axis...') 
		headerline=2
		om,Sig=Fileio.Read_complex_multilines('./ac/Sig.out',headerline)
		s_oo = None
		Vdc = None
		fi=open('./ac/Sig.out','r')
		for i in range(headerline):
			line=fi.readline()
			m=re.search('#(.*)',line)
			exec(m.group(1).strip())
		#s_oo_Vdc=array(s_oo)-array(Vdc)
		s_oo_Vdc=array((np.array(s_oo)).astype(np.float))-array((np.array(Vdc)).astype(np.float))

		ommesh=linspace(emin,emax,rom)
		Sig_tot=zeros((len(Sig),rom),dtype=complex)
		for i in range(len(Sig)):
			SigSpline = interpolate.splrep(om, Sig[i].real, k=1, s=0)
			Sig_tot[i,:] += interpolate.splev(ommesh, SigSpline)
			SigSpline = interpolate.splrep(om, Sig[i].imag, k=1, s=0)
			Sig_tot[i,:] += 1j*interpolate.splev(ommesh, SigSpline)

		fo=open('SigMdc.out','w')
		for i in range(5):
			if i==0 or i==3:
				fo.write('%18.15f ' %(s_oo_Vdc[0]))
			else:
				fo.write('%18.15f ' %(s_oo_Vdc[1]))
		if len(s_oo_Vdc)>5:
			fum=open('SigMdc_dn.out','w')
			for j in range(5):
				if j ==0 or j==3:
					fum.write('%18.15f ' %(s_oo_Vdc[2]))
				else:
					fum.write('%18.15f ' %(s_oo_Vdc[3]))
		header1='# nom,ncor_orb= '+str(len(ommesh))+' '+str(len(Sig_tot))
		#header2='# T= %18.15f'%(1.0/pC['beta'][0])#+str(self.T)
		header2='# T= %18.15f'%(broaden)#+str(self.T)
		header3='# s_oo-Vdc= '
		for i in range(len(s_oo_Vdc)):
			header3+='%18.15f '%(s_oo_Vdc[i])
		header4='# s_oo= '+str(s_oo)
		header5='# Vdc= '+str(Vdc)
		if dest_dir =='dos':
			Fileio.Print_complex_multilines(Sig_tot,ommesh,'./dos/sig.inp_real' ,[header1,header2,header3,header4,header5])

		#create sig.inp_real without header for old version of bandplotting
		if dest_dir =='bands':
			Fileio.Print_complex_multilines(Sig_tot,ommesh,'./bands/SigMoo_real.out')

		print('Interpolation complete.\n')


	def anal_cont(self,args):
		"""
		This method performs the analytic continuation.
		"""

   		siglistindx = args.siglistindx	

		#creating directory for ac
		if os.path.exists("ac"):
			shutil.rmtree("ac")
			os.makedirs("ac")
		else:	
			os.makedirs("ac")			

		#copying the last few self-energies from the DMFT run in the directory above
		siglist = sorted(glob.glob("sig.inp.*"),key=os.path.getmtime)[-siglistindx:]
		for file in siglist:
			shutil.copy(file,'ac')

		#averaging sef energies
		print('\nAveraging self-energies from: ')
		print(siglist)
		cmd = "cd ac && sigaver.py sig.inp.*"
		out, err = subprocess.Popen(cmd, shell=True,stdout = subprocess.PIPE, stderr = subprocess.PIPE).communicate()
		if err:
		 	print(err)
		 	print('Averaging self-energies Failed!\n')
		 	sys.exit()
		else:
		 	print('Self-energies averaged.\n')  
		  

		#copy maxent_params.dat from source if not in DMFT directory
		if os.path.exists("maxent_params.dat"):
		    shutil.copyfile('maxent_params.dat','./ac/maxent_params.dat')
		else:
		    src=self.path_bin+ os.sep+"maxent_params.dat"
		    shutil.copyfile(src,"./ac/maxent_params.dat")

		#Analytic continuation
		print('Running analytic continuation...')
		cmd = "cd ac && maxent_run.py sig.inpx"+" > ac.out 2> ac.error"
		out, err = subprocess.Popen(cmd, shell=True,stdout = subprocess.PIPE, stderr = subprocess.PIPE).communicate()
		if os.path.exists("./ac/Sig.out"):
		    print('Analytic continuation complete.\n')  
		else:
		    print('Analytic continuation failed! Check ac.error for details.\n') 
		    sys.exit()

	def Create_kpath(self,KPoints,nk_band):
		print('\nGenerating k-path...')
		def dist(a,b):
			return sqrt(sum((array(a)-array(b))**2))

		#returns the distance of given a and b points
		KPoints=array(KPoints)
		path_len=[]
		for i in range(len(KPoints)-1):
			path_len.append(dist(KPoints[i+1],KPoints[i]))
		path_nk=map(int,nk_band*array(path_len)/sum(path_len))
		klist=[]; dist_K=[0.]; dist_SK=[0.]
		for i,nkk in enumerate(path_nk):
			for n in range(nkk):
				klist.append(KPoints[i]+(KPoints[i+1]-KPoints[i])*n/nkk)
				if len(klist)>1: dist_K.append(dist_K[-1]+dist(klist[-1],klist[-2]))
			dist_SK.append(dist_SK[-1]+path_len[i])

		# Add the ending point
		klist.append(KPoints[-1])
		dist_K.append(dist_K[-1]+dist(klist[-1],klist[-2]))
		return array(klist), array(dist_K), array(dist_SK)
	
	def genksum(self,rom,kpband):	
		fp=open('./bands/ksum.input','w')
		fp.write('%d' %kpband)
		fp.write('\n%d' %rom)
		fp.write('\n%d' %p['nspin'])
		fp.write('\n%d' %5)
		fp.write('\n%d' %5)
		fp.write('\n%f' %0.01)
		fp.write('\n%d' %p['n_tot'])
		fp.write('\n%d' %p['mu_iter'])
		fp.close()

	def dos(self,args):	    
		""" 
		This method performs the Density of States calculation.
		"""

		dest_dir = 'dos'

		#creating directory for dos 
		if os.path.exists("dos"):
			shutil.rmtree("dos")
			os.makedirs("dos")
		else:	
			os.makedirs("dos")

		#copy Sig.out into /dos
		if self.checksig():
			shutil.copyfile('./ac/Sig.out','./dos/Sig.out')
		else:
			sys.exit()	

		#interpolating
		self.interpol(args.emin,args.emax,args.rom,args.broaden,dest_dir)	

		#copying files from DMFT directory to dos directory
		cmd = "cd dos && Copy_input_bands.py ../ -dos"
		out, err = subprocess.Popen(cmd, shell=True).communicate()
		if err:
			print('File copy failed!\n')
			print(err)
			sys.exit()
		else:
			print(out)

		#running dmft_dos.x
		print("Calculating DMFT DOS...")
		cmd ="cd dos && "+self.para_com+" "+"dmft_dos.x"
		out, err = subprocess.Popen(cmd, shell=True, stdout = subprocess.PIPE, stderr = subprocess.PIPE).communicate()
		if err:
			print(err)
			print('DMFT DOS calculation failed!\n')
			sys.exit()
		else:
			print('DMFT DOS calculation complete.\n')		

		if args.plot:
			self.plot_dos()	

	def plot_dos(self):
		"""
		This method plots the density of states plot. 
		"""

		print('Plotting DOS...')	
		with open('./dos/G_loc.out', 'r') as f:
			lines = f.readlines()
			x = [float(line.split()[0]) for line in lines]

			y_dz2 = [float(line.split()[2]) for line in lines]  #eg
			y_x2y2 = [float(line.split()[8]) for line in lines]


			y_dxz = [float(line.split()[4]) for line in lines]
			y_dyz = [float(line.split()[6]) for line in lines]  #t2g
			y_dxy = [float(line.split()[10]) for line in lines]

			yg= [float(line.split()[2])+float(line.split()[8]) for line in lines]
			tg= [float(line.split()[4])+float(line.split()[6])+float(line.split()[10]) for line in lines]

		y_eg =[-1*count/3.14 for count in yg]
		y_t2g =[-1*count/3.14 for count in tg]  
    
		plt.figure(1)
		plt.plot(x,y_eg,'r',label='$d-e_g$') 
		plt.plot(x,y_t2g,'b',label='$d-t_{2g}$') 
		plt.title('DMFT PDOS')  
		plt.xlabel('Energy (eV)')
		plt.ylabel('DOS (states eV/cell)')
		plt.axvline(x=0,color='gray',linestyle='--')
		plt.legend()
		plt.savefig('./dos/DMFT-PDOS.png')
		plt.show()
		f.close()		
				

	def bands(self,args):
		"""
		This method performs the band structure calculations.			
		"""
		dest_dir = 'bands'
		dummy_broaden = 0.03

		#creating directory for bands
		if os.path.exists("bands"):
			shutil.rmtree("bands")
			os.makedirs("bands")
		else:	
			os.makedirs("bands")

		#copy Sig.out into /bands
		if self.checksig():
			shutil.copyfile('./ac/Sig.out','./bands/Sig1.out')
		else:
			sys.exit()	

		#interpolating
		self.interpol(args.emin,args.emax,args.rom,dummy_broaden,dest_dir)

		print('kpband=',args.kpband)
		print('kplits=',args.kplist)
		print('knames=',args.knames)

		#generating k-path
		klist, dist_K, dist_SK = self.Create_kpath(args.kplist,args.kpband)
		fi=open('./bands/klist.dat','w')
		for i in range(args.kpband):
			kcheck=0
			for j,d in enumerate(dist_SK):
				if abs(dist_K[i]-d)<1e-4: 
					print >>fi, '%.14f  %.14f  %.14f  %.14f  %s' %(dist_K[i],klist[i][0],klist[i][1],klist[i][2],args.knames[j])
					kcheck=1
					break
			if kcheck==0:
				print >>fi, '%.14f  %.14f  %.14f  %.14f' %(dist_K[i],klist[i][0],klist[i][1],klist[i][2]) 
		print('k-path generated.')
    

    	#copying files from DMFT directory to dos directory
		cmd = "cd bands && Copy_input_bands.py ../ -bands"
		out, err = subprocess.Popen(cmd, shell=True).communicate()
		if err:
			print('File copy failed!\n')
			print(err)
			sys.exit()
		else:
			print(out)


		#generating ksum.input
		self.genksum(args.rom,args.kpband)		

		#running dmft_ksum_band 
		print("Calculating band structure")
		cmd ="cd bands && "+self.para_com+" "+"dmft_ksum_band"
		out, err = subprocess.Popen(cmd, shell=True, stdout = subprocess.PIPE, stderr = subprocess.PIPE).communicate()
		if err:
			print(err)
			print('Band structure calculation failed!\n')
			sys.exit()
		else:
			print('Band structure calculation complete.\n')

	def plot_plain_bands(self):
		"""
		This method plots the regular DMFT band structure.
		"""

		vmm = [0,5.0]
		nk=0
		SKP=[]
		SKPoints=[]
		distk=[]
		kpts=[]
		fi=open('./bands/klist.dat','r')
		for line in fi.readlines():
			line=line.split()
			distk.append(float(line[0]))
			kpts.append([float(line[1]),float(line[2]),float(line[3])])
			if len(line)==5:
				SKP.append(float(line[0]))
				SKPoints.append(line[4])
		fi.close() 

		fi=open('./bands/ksum.input','r')
		numk=int(fi.readline())
		print("numk=",numk)
		nom=int(fi.readline())
		print("nom=",nom)
		fi.close()
		A_k=[]
		dist_k=[]
		om=[]
		kpts=[]
		fi=open('./bands/Gk.out','r')
		for i in range(numk):
			kpts.append(list(map(float,fi.readline().split()[1:])))
			A_k.append([]) 
			om.append([]) 
			for j in range(nom):
				line=list(map(float,fi.readline().split()))
				A_k[i].append(-1*line[2]/3.14159265)
				om[i].append(line[0])
			A_k[i]=np.array(A_k[i])
		fi.close()

		A_k=np.transpose(A_k)[::-1]

		(ymin,ymax) = (om[0][0],om[0][-1])
		(xmin,xmax) = (distk[0],distk[-1])

		im=plt.imshow(A_k,cmap=cm.hot, vmin=vmm[0], vmax=vmm[1], extent=[xmin,xmax,ymin,ymax],aspect='auto')
		colorbar(im,orientation='vertical',pad=0.05,shrink=1.0,ticks=arange(0,10.0,1.0))
		xticks(SKP,SKPoints)
		xlabel('k-path',fontsize='xx-large')
		ylabel('Energy',fontsize='xx-large')
		axhline(y=0,color='black',ls='--')

		show()
		savefig('./bands/A_k.eps')

	def plot_partial_bands(self,wan_orbs):	
		"""
		This method plots partial bands for orbitals. The order of the orbitals is the Wannier orbital order. 
		"""

		vmm = [0,10]
		SKP=[]
		SKPoints=[]
		distk=[]
		kpts=[]
		fi=open('./bands/klist.dat','r')
		for line in fi.readlines():
			line=line.split()
			distk.append(float(line[0]))
			kpts.append([float(line[1]),float(line[2]),float(line[3])])
			if len(line)==5:
				SKP.append(float(line[0]))
				SKPoints.append(line[4])
		fi.close() 

		fi=open('./bands/ksum.input','r')
		numk=int(fi.readline())
		print("numk=",numk)
		nom=int(fi.readline())
		print("nom=",nom)
		fi.close()

		A_k=[]
		dist_k=[]
		om=[]

		fi_gk=open('./bands/Gk_partial.out','r')
		data=re.findall('k=\s*[0-9E+-.\sorb=\s]*',fi_gk.read())
		fi_gk.close()
		filtered_orbs=[]

		for i in range(numk):    
			#kpts.append(list(map(float,data[i].split('\n')[0].split()[1:]))) 
         
   
			for orbs in wan_orbs:          
				filtered_orbs.append(data[i].split('\n')[1:][(orbs-1)*nom+orbs:orbs*nom+orbs])
       
		for orb_counter in range(numk*len(wan_orbs)):
			for j in range(nom): 
				A_k.append(-1*float(filtered_orbs[orb_counter][j].split()[2])/3.14159265)
				om.append(float(filtered_orbs[orb_counter][j].split()[0]))

		A_k=np.array(A_k)
		A_k=A_k.reshape(numk,nom*len(wan_orbs))  

		A_kblend=np.zeros((len(wan_orbs),numk,nom))
		A_ktotal=np.zeros((numk,nom))

		nom_counter=0
		for orb in range(len(wan_orbs)):
			A_kblend[orb,:,:] = A_k[:,nom_counter:nom_counter+nom]
    		nom_counter=nom_counter+nom
    		A_ktotal=A_ktotal+A_kblend[orb,:,:]

		A_ktotal = np.transpose(A_ktotal)[::-1]    

		om=np.array(om)
		om=om.reshape(numk,nom*len(wan_orbs))

		(ymin,ymax) = (om[0][0],om[0][-1]) #500x100 energy matrix
		(xmin,xmax) = (distk[0],distk[-1])

		im = plt.imshow(A_ktotal,cmap=cm.hot,extent=[xmin,xmax,ymin,ymax],aspect='auto',vmin=vmm[0],vmax=vmm[1])

		colorbar(im,orientation='vertical',pad=0.05,shrink=1.0,ticks=arange(0,10.0,1.0))
		xticks(SKP,SKPoints)
		xlabel('k-path',fontsize='xx-large')
		ylabel('Energy',fontsize='xx-large')
		axhline(y=0,color='black',ls='--')


		plt.show()
		plt.savefig('./bands/A_k_partial.eps')

if __name__ == "__main__":

	#top level parser
	print('\n--------------------------------- \n| DMFTwDFT post-processing tool |\n---------------------------------\n')
	des = 'This tool performs Analytic Contiunation, Density of States and Band structure calculations from DMFTwDFT outputs.' 
	parser = argparse.ArgumentParser(description=des,formatter_class=RawTextHelpFormatter)
	subparsers = parser.add_subparsers(help = 'sub-command help')

	#parser for ac
	parser_ac = subparsers.add_parser('ac',help = 'Analytic Continuation')
	parser_ac.add_argument('-siglistindx',default=2, type=int, help='How many last self energy files to average?')
	parser_ac.set_defaults(func=PostProcess().anal_cont)	

	#parser for dos
	parser_dos = subparsers.add_parser('dos',help = 'DMFT Density of States')
	parser_dos.add_argument('-emin',default=-5.0, type=float, help='Minimum value for interpolation')
	parser_dos.add_argument('-emax',default=5.0, type=float, help='Maximum value for interpolation')
	parser_dos.add_argument('-rom',default=1000, type=int, help='Matsubara Frequency (omega) points')
	parser_dos.add_argument('-broaden',default=0.03, type=float, help='Broadening')
	parser_dos.add_argument('-plot',action='store_true', help='Plot the density of states?')
	parser_dos.set_defaults(func=PostProcess().dos)

	#parser for bands 
	parser_bands = subparsers.add_parser('bands',help = 'DMFT Bandstructure')
	parser_bands.add_argument('-emin',default=-5.0, type=float, help='Minimum value for interpolation')
	parser_bands.add_argument('-emax',default=5.0, type=float, help='Maximum value for interpolation')
	parser_bands.add_argument('-rom',default=1000, type=float, help='Matsubara Frequency (omega) points')
	parser_bands.add_argument('-sp',action='store_true', help='Spin polarized calculation?')
	parser_bands.add_argument('-kpband',default=3500,type=int,help='Number of k-points for band structure calculation')
	parser_bands.add_argument('-knames',default=['$\Gamma$','X','M','$\Gamma$','R'],type=str,nargs='+',help='Names of the k-points')
	parser_bands.add_argument('-kplist',default=[[0,0,0],[0.5,0,0],[0.5,0.5,0],[0,0,0],[0.5,0.5,0.5]],type=int,nargs='+',action='append',help='List of k-points as an array')
	parser_bands.set_defaults(func=PostProcess().bands)

	args = parser.parse_args()
	args.func(args)
