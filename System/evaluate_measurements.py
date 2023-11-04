# -*- coding: utf-8 -*-
"""
Created on Sun Oct 22 12:39:44 2023

@author:  BastelBaus
@Content: Script to plot and evaluate different magnet measurements 
          from a SimpleFull6DSPaceKnob device

Link: Magnetic Sensor Calibrataion Algorithms: https://www.ncbi.nlm.nih.gov/pmc/articles/PMC8401862/

"""


import csv
import numpy as np
import matplotlib.pyplot as plt

FILENAME = 'C:\\Users\\pagantroll\\Dokumente\\GitHub\\Simple6DSpaceKnob\\System\\data\\FullKnob_3D.csv'

def meanLength(vec):
    if vec.shape[0] == 3: return np.mean( np.sqrt( np.square(vec[0,:]) + np.square(vec[1,:]) + np.square(vec[2,:])  ))
    else: return np.mean( np.sqrt( np.square(vec[:,0]) + np.square(vec[:,1]) + np.square(vec[:,2])  ))
    

class MagneticSensor:
    col  = ['.r','.b','.g']  # just a color vector
    
    n = 0                    # number of samples
    s = 1                    # sensitivity in [LSB/G]
    
    dataRaw         = None   # the raw measurement data    
    fieldVec        = None   # absolut length of vector, non calibrated
    rotVec          = None   # vector holding the 3 rotation angles  
    meanFieldVec    = None   # mean magnetic field over the full measurement
    stdFieldVec     = None   # mean magnetic field over the full measurement
     
    dataCal         = None   # the calibrated measurement data
    fieldVecCal     = None   # absolut length of vector, non calibrated
    rotVecCal       = None   # vector holding the 3 rotation angles
    meanFieldVecCal = None   # mean magnetic field over the full measurement
    stdFieldVecCal  = None   # mean magnetic field over the full measurement
    
    
    
    def __init__(self, data,sensitivity=1):
        self.setMeasurements(data,sensitivity)
    
    def setMeasurements(self,data,sensitivity=1):       
        self.dataRaw = data
        self.n       = data.shape[1]
        self.s       = sensitivity

    def setTime(self,timestamps):
        self.tm = timestamps

    def calculateAll(self, targetField=1):
        self.fieldVec  = np.sqrt( np.square(self.dataRaw[0]) + np.square(self.dataRaw[1]) + np.square(self.dataRaw[2]) )
        self.meanFieldVec = np.mean(self.fieldVec)
        self.stdFieldVec  = np.std(self.fieldVec)
        self.rotVec       = np.asmatrix( [ np.arctan2(self.dataRaw[0], self.dataRaw[1])*180/np.pi,
                                           np.arctan2(self.dataRaw[0], self.dataRaw[2])*180/np.pi,
                                           np.arctan2(self.dataRaw[1], self.dataRaw[2])*180/np.pi ] )

        self.estimateCalibration(targetField)
        self.applyCalibration()

        self.fieldVecCal  = np.sqrt( np.square(self.dataCal[0]) + np.square(self.dataCal[1]) + np.square(self.dataCal[2]) )
        self.meanFieldVecCal = np.mean( self.fieldVecCal )
        self.stdFieldVecCal  = np.std(self.fieldVecCal)
        self.rotVecCal = np.asmatrix( [ np.arctan2(self.dataCal[0], self.dataCal[1])*180/np.pi,
                                        np.arctan2(self.dataCal[0], self.dataCal[2])*180/np.pi,
                                        np.arctan2(self.dataCal[1], self.dataCal[2])*180/np.pi ] )
                                                                                                        
        self.printStats()
    
    def loadRaw(self,filename="data/mag.txt"):
        ' Load a file and stores '
        result = [] 
        with open(filename, newline='') as csvfile:    
            spamreader = csv.reader(csvfile, delimiter='\t', quotechar='|')
            for i,row in enumerate(spamreader):
                if len(row) != 3: continue
                dat = [float(row[0]),float(row[1]),float(row[2])];
                #print(i,":",dat)
                result.append(dat)
                
        result = np.asfarray(result)
        result = np.transpose(result)
        self.__setMeasurements(result)
        
    def saveRaw(self,filename="output.txt"):
        with open(filename, "w") as text_file:
            for k in range(self.n):
                print(f"{self.dataRaw[0][k]/self.s}\t"
                      f"{self.dataRaw[1][k]/self.s}\t"
                      f"{self.dataRaw[2][k]/self.s}\t", file=text_file)

        
    def printStats(self):
        print('------- Statistics -------')
        print('sensitivity            :',self.s,' [LSB/GAUSS]')
        print('samples                :',self.n)
        print('mean field vector (raw):',np.round(self.meanFieldVec/self.s*1000)/1000,'GAUSS +/-',np.round(self.stdFieldVec/self.s*1000),'mGAUSS')
        print('mean field vector (cal):',np.round(self.meanFieldVecCal/self.s*1000)/1000,'GAUSS +/-',np.round(self.stdFieldVecCal/self.s*1000),'mGAUSS')
        
    
    def applyCalibration(self):
        
        self.dataCal = np.zeros(self.dataRaw.shape)
        for k in range(self.n): # toDo as matrix
            self.dataCal[0:3,k] = np.matmul(self.Ai, self.dataRaw[0:3,k] - self.b) / (self.meanFieldVec / self.s )


    def estimateCalibration(self,targetField=1,debug=False):

        
        def dprint(*a):
            if debug: print(*a)
            
        # Implementation of calibration algo
        # References:
        # https://sites.google.com/view/sailboatinstruments1/d-implementation
        # https://de.mathworks.com/matlabcentral/fileexchange/23377-ellipsoid-fitting
        # https://github.com/millerlp/Rmagneto/blob/master/Rmagneto.c
        # https://github.com/beattiea/TiltyIMU/blob/master/Tilty%20Software/Processing/Experiments/Testing%20Magnetometer%20calibration/ellipsoid_fit/ellipsoid_fit.m

        if 1==0: # Magneto 1.2 test file results
            self.b = np.asarray([-0.021659, 0.013250, -0.026167]); 
            
        if 1==0:  # my test file results
            self.b = np.asarray([0.049905, 0.128849, 0.044358]); 
            self.Ai = np.asmatrix([[ 2.177104, -0.014507,  0.011303],
                                   [-0.014507,  2.149547,  0.022436],
                                   [ 0.011303,  0.022436,  2.161512]])
            
        x = self.dataRaw[0]#/self.s
        y = self.dataRaw[1]#/self.s
        z = self.dataRaw[2]#/self.s
                    
        dprint("x data:",x)
        dprint("y data:",y)
        dprint("z data:",z)
        
        D = np.zeros( (9,self.n))
        for i in range(self.n): # todo, replace by matrix operations
            D[0][i] = x[i] * x[i];
            D[1][i] = y[i] * y[i];
            D[2][i] = z[i] * z[i];
            D[3][i] = 2.0 * y[i] * z[i];
            D[4][i] = 2.0 * x[i] * z[i];
            D[5][i] = 2.0 * x[i] * y[i];
            D[6][i] = 2.0 * x[i];
            D[7][i] = 2.0 * y[i];
            D[8][i] = 2.0 * z[i];
        dprint("D:",D)
        
        # https://github.com/beattiea/TiltyIMU/blob/master/Tilty%20Software/Processing/Experiments/Testing%20Magnetometer%20calibration/ellipsoid_fit/ellipsoid_fit.m
        # v = ( D' * D ) \ ( D' * ones( size( x, 1 ), 1 ) );
            # Octave: B \ b
            # Python: x,resid,rank,s = np.linalg.lstsq(B,b)
        B = np.matmul(D,D.transpose())
        b = np.matmul(D,np.ones(self.n))        
        v,resid,rank,s  = np.linalg.lstsq(B,b, rcond=None)
        dprint("v:",v)
       
        # https://github.com/beattiea/TiltyIMU/blob/master/Tilty%20Software/Processing/Experiments/Testing%20Magnetometer%20calibration/ellipsoid_fit/ellipsoid_fit.m
        # A = [ v(1) v(4) v(5) v(7); ...
        #       v(4) v(2) v(6) v(8); ...
        #       v(5) v(6) v(3) v(9); ...
        #       v(7) v(8) v(9) -1 ];
        Q = np.zeros(16)
        Q[ 0] = v[0];
        Q[ 1] = v[3]; 
        Q[ 2] = v[4];
        Q[ 3] = v[6]; 
        Q[ 4] = v[3];
        Q[ 5] = v[1]; 
        Q[ 6] = v[5];
        Q[ 7] = v[7]; 
        Q[ 8] = v[4];
        Q[ 9] = v[5];
        Q[10] = v[2];
        Q[11] = v[8];
        Q[12] = v[6];
        Q[13] = v[7];
        Q[14] = v[8];
        Q[15] = -1;
        Q = Q.reshape((4,4))
        dprint('\nQ:',Q)
            
        center,resid,rank,s  = np.linalg.lstsq(- Q[0:3,0:3], [ v[6] , v[7] , v[8] ] ,rcond=None)
        self.b = center
        dprint("b=",self.b)

        #% form the corresponding translation matrix
        T = np.eye(4,4)
        T[3,0:3] = center
        dprint("T:", T)
        #% translate to the center
        R = np.matmul(np.matmul(T,Q),T.transpose())
        dprint("R:", np.round(R*1000)/1000)

        # solve the eigenproblem
        [ evals, evecs]= np.linalg.eig( -R[0:3,0:3]/R[3,3]) 
        dprint("evals :",evals)
        dprint("evecs :",evecs)
        radii = np.sqrt( np.reciprocal(evals) )
        dprint("radii:",radii)
        dprint("Norm RADII:",np.linalg.norm(radii))
        

        # do ellipsoid fitting
        #scale = np.linalg.inv( np.diag(radii) ) * np.min(radii) 
        scale = np.linalg.inv( np.diag(radii) ) 
        comp = np.matmul(np.matmul(evecs,scale),evecs.transpose())        
        
        nDat = np.mean( np.sqrt( np.square(x) + np.square(y) + np.square(z) ))
        print("Norm Dat: ", nDat )
        
        A = np.asmatrix([x - self.b[0],
                         y - self.b[1],
                         z - self.b[2]])
        
        # notrmalize
        G = np.matmul(comp,A)
        nG = np.mean( np.sqrt( np.square(G[0]) + np.square(G[1]) + np.square(G[2]) ))
        dprint("G :",G)
        print("Norm: ", nG )
        
        self.Ai = comp  * ( targetField / nG * nDat ) 
        dprint("Final results:")
        dprint("b  =",self.b)
        dprint("Ai =",self.Ai)

        return

    
    def plot3D(self,ax=None):
         
         fig = plt.figure(figsize=plt.figaspect(1.))
         ax = fig.add_subplot(2,2,1,projection='3d')
         ax.plot(self.dataRaw[0,:]/self.s,self.dataRaw[1,:]/self.s,self.dataRaw[2,:]/self.s,'r')
         ax.plot(self.dataCal[0,:]/self.s,self.dataCal[1,:]/self.s,self.dataCal[2,:]/self.s,'g')
         #plt.show()
         ax.set_xlim(-0.6,0.6)
         ax.set_ylim(-0.6,0.6)
         ax.set_zlim(-0.6,0.6)
         ax.set_box_aspect([1.0, 1.0, 1.0])
         ax.set_aspect('equal')
         ax.set_proj_type('ortho')
         
         k1 = [0,0,1]; k2 = [1,2,2]
         k3 = ['Bx','Bx','By']
         k4 = ['By','Bz','Bz']
               
         for k in range(3):
             ax = fig.add_subplot(2,2,2+k)
             ax.plot(self.dataRaw[k1[k],:]/self.s,self.dataRaw[k2[k],:]/self.s,'r')
             ax.plot(self.dataCal[k1[k],:]/self.s,self.dataCal[k2[k],:]/self.s,'g')
             t = np.deg2rad( np.asarray(range(3601))/10)
             ax.plot(0.5*np.sin(t),0.5*np.cos(t),'k')
             ax.set_xlim(-0.6,0.6)
             ax.set_ylim(-0.6,0.6)             
             ax.set_aspect('equal')
             ax.set_xlabel(k3[k])
             ax.set_ylabel(k4[k])
             ax.grid('on')

    
    def plotTimeSignal(self,inLSB = False):
        if inLSB: s =1 
        else:     s = self.s
        
        fig,axs = plt.subplots(2,2)
        a1 = axs[0][0]; a2 = axs[1][0]
        a3 = axs[0][1]; a4 = axs[1][1]
        
        a1.plot(self.dataRaw[0]/s,'r');
        a1.plot(self.dataRaw[1]/s,'g');
        a1.plot(self.dataRaw[2]/s,'b');
        a1.plot(self.fieldVec/s,'k');
        a1.legend(['Bx','By','Bz','abs(B)'],loc="center right")
        a1.set_title('raw')
        a1.grid('on')
        if inLSB:
            a1.set_ylabel('signal [LSB]')
            a1.set_ylim(-2000,2000)
        else: 
            a1.set_ylabel('signal [GAUSS]')
            a1.set_ylim(-2000/s,2000/s)

        a2.set_xlabel('samples')
        a2.plot(self.rotVec[0].transpose(),'r');
        a2.plot(self.rotVec[1].transpose(),'g');
        a2.plot(self.rotVec[2].transpose(),'b');
        a2.legend(['Bx->By','Bx->Bz','By->Bz'],loc="center right")
        a2.set_ylabel('angle [°]')
        a2.set_ylim(-200,200)
        a2.grid('on')
        
        # Calibrated data
        
        a3.plot(self.dataCal[0]/s,'r');
        a3.plot(self.dataCal[1]/s,'g');
        a3.plot(self.dataCal[2]/s,'b');
        a3.plot(self.fieldVecCal/s,'k');
        a3.set_title('calibrated')
        a3.legend(['Bx','By','Bz','abs(B)'],loc="center right")
        if inLSB:
            a3.set_ylabel('signal [LSB]')
            a3.set_ylim(-2000,2000)
        else: 
            a3.set_ylabel('signal [GAUSS]')
            a3.set_ylim(-2000/s,2000/s)
        a3.grid('on')
            
        a4.set_xlabel('samples')
        a4.plot(self.rotVecCal[0].transpose(),'r');
        a4.plot(self.rotVecCal[1].transpose(),'g');
        a4.plot(self.rotVecCal[2].transpose(),'b');
        a4.legend(['Bx->By','Bx->Bz','By->Bz'],loc="center right")
        a4.set_ylabel('angle [°]')
        a4.set_ylim(-200,200)
        a4.grid('on')

        # finished
        fig.show();
        

class SimpleFull6DSpaceKnob:
    # properties of magnetic sensor
    mag_sens_low  =  3000 # [LSB/G] Sensitivity of magnetometer [8G Range] // mgPerDigit = 4.35f
    mag_sens_high = 12000 # [LSB/G] Sensitivity of magnetometer [2G Range] // mgPerDigit = 1.22f
    # mag_sens_mT = mag_sens/10 # [LSB/mT] convert GAUSS to TEslas: 1G = 10-4T ==> 1G = 10mT
    col = ['.r','.b','.g']
    
    ms = [None,None,None]  # Magnetic Sensors Class
    
    def loadFile(self,filename):
        ' Load a file and stores '
        result = [] 
        timestamp =  []
        with open(filename, newline='') as csvfile:    
            spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
            for row in spamreader:
                if not row[1].isnumeric(): continue
                tm = row[1]
                sensors = row[2:-1]
                #print(tm,' ==> ',sensors)
                result.append(sensors)
                timestamp.append(tm)
                
        result = np.asfarray(result)
        result = np.transpose(result)
        self.ms[0] = MagneticSensor(( result[0:3]), self.mag_sens_low)
        self.ms[1] = MagneticSensor(( result[3:6]), self.mag_sens_low)
        self.ms[2] = MagneticSensor(( result[6:9]), self.mag_sens_low)
                
        timestamp = np.asfarray(timestamp) 
        timestamp = timestamp- timestamp[0]
        self.ms[0].setTime(timestamp)
        self.ms[1].setTime(timestamp)
        self.ms[2].setTime(timestamp)

    def doEvaluation(self,filename):
        pass



if __name__ == '__main__':
    
   
    plt.close('all')
    
    sf6d = SimpleFull6DSpaceKnob()
    sf6d.loadFile(FILENAME)
    #sf6d.ms[0].loadRaw()
    #for k in range(3): sf6d.ms[k].saveRaw()


    for k in range(3): 
        sf6d.ms[k].calculateAll(0.5)
        sf6d.ms[k].plotTimeSignal()    
        sf6d.ms[k].plot3D()
        
    fig,axs = plt.subplots(3) 
    col = ['r','g','b']
    cor = [120,0,0]
    
    ss = [1,-1,0]
    for s in range(3): 
        alpha = ss[s]*120
        ca = np.cos(np.deg2rad(alpha))
        sa = np.sin(np.deg2rad(alpha))    
        #rmat  = np.asmatrix ( [[1,0,0], [0,ca,-sa], [0,sa,ca] ] )
        #rmat  = np.asmatrix ( [[ca,0,sa], [0,1,0], [-sa,0,ca] ] )
        rmat  = np.asmatrix ( [[ca,-sa,0], [sa,ca,0], [0,0,1] ] )        
        #print(rmat)
        
        rotvec = np.zeros( (3,sf6d.ms[s].n))   
        for i in range(sf6d.ms[s].n): 
            v = sf6d.ms[s].dataCal[:,i]
            rotvec[:,i] = np.dot(rmat,v.transpose())
        
        sig = [ np.rad2deg(np.arctan2( rotvec[0,:],rotvec[1,:])),
                np.rad2deg(np.arctan2( rotvec[0,:],rotvec[2,:])),
                np.rad2deg(np.arctan2( rotvec[1,:],rotvec[2,:]))]
                           
        for k in range(3): axs[k].plot(sig[k],col[s])
        
        
    axs[0].legend(['sensor 1','sensor 2','sensor 3'])
    axs[0].set_ylabel('Bx->By [°]')
    axs[1].set_ylabel('Bx->Bz [°]')
    axs[2].set_ylabel('By->Bz [°]')
    axs[2].set_xlabel('samples')
    plt.show()

   
