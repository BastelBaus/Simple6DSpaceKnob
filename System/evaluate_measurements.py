# -*- coding: utf-8 -*-
"""
Created on Sun Oct 22 12:39:44 2023

@author:  BastelBaus
@Content: Script to plot and evaluate different magnet measurements 
          from a SimpleFull6DSPaceKnob device

"""


import csv
import numpy as np
import matplotlib.pyplot as plt

FILENAME = 'C:\\Users\\pagantroll\\Dokumente\\GitHub\\Simple6DSpaceKnob\\System\\data\\FullKnob_LongTerm.csv'
#FILENAME = 'C:\\Users\\pagantroll\\Dokumente\\GitHub\\Simple6DSpaceKnob\\System\\data\\FullKnob_3D.csv'


class SimpleFull6DSpaceKnob:
    # properties of magnetic sensor
    mag_sens_low  =  3000 # [LSB/G] Sensitivity of magnetometer [8G Range] // mgPerDigit = 4.35f
    mag_sens_high = 12000 # [LSB/G] Sensitivity of magnetometer [2G Range] // mgPerDigit = 1.22f
   # mag_sens_mT = mag_sens/10 # [LSB/mT] convert GAUSS to TEslas: 1G = 10-4T ==> 1G = 10mT
    
    
    def loadFile(self,filename):
        ' Load a file and stores '
        result = [] 
        with open(filename, newline='') as csvfile:    
            spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
            for row in spamreader:
                #timestamp = row[0]
                #print(">>",timestamp[3:]);
                #return
                result.append(row[1:-1])
        result = np.transpose(np.asfarray(result));    
        self.sensors   = [ result[ 0: 3], result[ 3: 6], result[ 6: 9]] 
        self.sensors0  = [ result[ 9:12], result[12:15], result[15:18]] 
        self.transform = result[18:21]
        self.temp      = result[21]  
        self.n = len(sf6d.temp);
    
    def plotMagnetSignals(self,i=0):
        plt.plot(self.sensors[i][0],'r');
        plt.plot(self.sensors[i][1],'g');
        plt.plot(self.sensors[i][2],'b');
        plt.xlabel('samples')
        plt.ylabel('signal [LSB]')
        plt.ylim(-2000,2000)
        plt.show();

    def printMagnetStats(self,i=0, s = mag_sens_low):
        print('x(',i,'): ', np.mean( self.sensors[i][0])/s, 'G  std: ', np.std( self.sensors[i][0])/s,'G') ;
        print('y(',i,'): ', np.mean( self.sensors[i][1])/s, 'G  std: ', np.std( self.sensors[i][1])/s,'G') ;
        print('z(',i,'): ', np.mean( self.sensors[i][2])/s, 'G  std: ', np.std( self.sensors[i][2])/s,'G') ;
        tmp = np.sqrt((np.square(self.sensors[i][0])+np.square(self.sensors[i][1])+np.square(self.sensors[i][2])));
        print('vec:  ', np.mean(tmp)/s, 'G  std: ', np.std(tmp) /s,'G' ) ;
        
        
    def plot3D():
        a = [0.2806795823, 0.1255472915, 0.405563324]
        b = [-0.0313555997, 0.2327507345,0.3872412045]
        c = [ -0.2179815312,-0.1960747349,0.3330111959]

        ax = plt.figure().add_subplot(projection='3d')

        ax.plot([0,a[0],a[0],a[0]],[0,0,a[1],a[1]],[0,0,0,a[2]],'b')
        ax.plot([0,a[0]],[0,a[1]],[0,a[2]],'r')


        ax.plot([0,b[0],b[0],b[0]],[0,0,b[1],b[1]],[0,0,0,b[2]],'--b')
        ax.plot([0,b[0]],[0,b[1]],[0,b[2]],'--r')

        ax.plot([0,c[0],c[0],c[0]],[0,0,c[1],c[1]],[0,0,0,c[2]],':b')
        ax.plot([0,c[0]],[0,c[1]],[0,c[2]],':r')

        ax.set_xlim(-0.4,0.4)
        ax.set_ylim(-0.4,0.4)
        ax.set_zlim(-0.4,0.4)

        plt.show()
        
        
    def findOffsets(self,i=0):
        m0 = 10000; t = (0,0,0)
    
        minAll = (-2000,-2000,-2000);
        maxAll = (2000,2000,2000);
        
        for k in [1,2,3,4,5,6]:
            tmp = minAll; minAll = maxAll;maxAll=tmp;        
            print('\nStep:',k,'m0: ',m0)
            print('maxAll: ',maxAll)
            print('minAll: ',minAll)
            print('steps:', ( round((minAll[0]-maxAll[0])/20), 
                              round((minAll[1]-maxAll[1])/20), 
                              round((minAll[2]-maxAll[2])/20)))
            mminAll =minAll; mmaxAll = maxAll;
            m = m0
            c = np.empty(0)
            for x in range(maxAll[0],minAll[0],round((minAll[0]-maxAll[0])/20)):
             for y in range(maxAll[1],minAll[1],round((minAll[1]-maxAll[1])/20)):
              for z in range(maxAll[2],minAll[2],round((minAll[2]-maxAll[2])/20)):
                ofs = (x,y,z)
                #a = (result[:,0:3]-np.concatenate((np.ones((n,1))*ofs[0],np.ones((n,1))*ofs[1],np.ones((n,1))*ofs[2]),axis=1));
                #b = np.sqrt((np.square(a[:,0])+np.square(a[:,1])+np.square(a[:,2])));    
                b  = np.sqrt(
                         np.square(self.sensors[i][0]-np.ones((self.n,1))*ofs[0]) +
                         np.square(self.sensors[i][1]-np.ones((self.n,1))*ofs[1]) +
                         np.square(self.sensors[i][2]-np.ones((self.n,1))*ofs[2])
                        )
                
                v = np.std(b);
                c = np.append(c, v)
                if v < m0: 
                    #print(x,'/',y,'/',z,' = ', v)   
                    mmaxAll = (max(mmaxAll[0],x),max(mmaxAll[1],y),max(mmaxAll[2],z))
                    mminAll = (min(mminAll[0],x),min(mminAll[1],y),min(mminAll[2],z))
                if v<m: m=v; t = (x,y,z) 
                
            print('min x/y/z = ',t,' : val= ',m)
            print(mminAll,mmaxAll)
            maxAll =mmaxAll; minAll = mminAll;
            plt.plot(c)
            plt.show();
            m0 = m*1.2
            
        return t        
        
        
    def printData(result,ofs):
            n = result.shape[0];
            a = (result[:,0:3]-np.concatenate((np.ones((n,1))*ofs[0],np.ones((n,1))*ofs[1],np.ones((n,1))*ofs[2]),axis=1));
            aa = np.sqrt((np.square(a[:,0])+np.square(a[:,1])+np.square(a[:,2])));
            print(np.mean(aa)/3000 ,'G field strength and std of ', np.std(aa)/3000,'G')    
            #a = (result[:,:])/mag_sens;
            plt.plot((((a[:,0]))),'r');
            plt.plot((((a[:,1]))),'g');
            plt.plot((((a[:,2]))),'b');
            plt.plot(aa,'k');
            plt.xlabel('sample')
            plt.ylabel('signal [mT]')
            plt.ylim(-2000,2000)
            plt.show();
    

    
            
    def main():
        print("python main function")
    
        result = loadFile();
        #result = np.concatenate((result,np.arctan(result/1000000)),axis=1)
        print(result.shape)
        
        #print(result)
        #plt.plot((result[:,:]-np.mean(result,axis=0,keepdims=True))/mag_sens);
        #plt.ylim(-100,100)
        #plt.xlabel('sample')
        #plt.ylabel('signal [mT]')
        #plt.show();
        print(np.mean(result,axis=0))
        
        a = result[:,:];
        a = (result[:,:]-np.mean(result,axis=0,keepdims=True));
        
        ofs = (-654, 532, 1220)  
        ofs = (-236, -236, 1038)
        ofs = (0, 0, 0)
        ofs = findOffsets(result[:,0:3])
        printData(result[:,0:3],ofs)
    
        ofs = (0,0,0)
        ofs = findOffsets(result[:,3:6])
        printData(result[:,3:6],ofs)
    
        ofs = (229, -150, 1199)
        ofs = (0, 0, 0)
        ofs = findOffsets(result[:,6:9])
        printData(result[:,6:9],ofs)
    
           
        return result
    

    def estimateCalibration(self,i=0):
        
        ofs = self.estimateOffset(i)
        
        scale = (1,1,1)
        oall = []; tall = [];
        for ox in range(-300,100,5):
         for oy in range(-300,100,5):
          for oz in range(-300,100,5):
            b  = np.std(
                  np.sqrt( np.square(scale[0]*(self.sensors[i][0]-ofs[0]-ox)) +
                           np.square(scale[1]*(self.sensors[i][1]-ofs[1]-oy)) +
                           np.square(scale[2]*(self.sensors[i][2]-ofs[2]-oz))
                    )
                  )
            oall.append(b)
            tall.append((ox,oy,oz))
         print(ox,' ' ,oy,' ',oz,' = ',b)
        mi =  np.argmin(oall)
        print('min index: ',mi,oall[mi],tall[mi] )
        plt.plot(oall); plt.show();
        
        print(ofs,tall[mi])
        return tall[mi]
        
    def estimateOffset(self,i=0):
        return (  (np.max(self.sensors[i][0])+np.min(self.sensors[i][0]))/2, 
                  (np.max(self.sensors[i][2])+np.min(self.sensors[i][1]))/2, 
                  (np.max(self.sensors[i][1])+np.min(self.sensors[i][2]))/2
               )
                    

        
    def plotCalibration(self,i=0,ofs=(0,0,0)):
 
         plt.plot(self.sensors[i][0]-ofs[0],self.sensors[i][1]-ofs[1],'.r')
         plt.plot(self.sensors[i][0]-ofs[0],self.sensors[i][2]-ofs[2],'.g')
         plt.plot(self.sensors[i][1]-ofs[1],self.sensors[i][2]-ofs[2],'.b')
         plt.xlim(-2000,2000)
         plt.ylim(-2000,2000)
         plt.grid(True)
         plt.show()       
         
         ax = plt.figure().add_subplot(projection='3d')
         ax.plot(self.sensors[i][0]-ofs[0],self.sensors[i][1]-ofs[1],self.sensors[i][2]-ofs[2],'.b')
         plt.show()
         ax.set_xlim(-2000,2000)
         ax.set_ylim(-2000,2000)
         ax.set_zlim(-2000,2000)
       
        


if __name__ == '__main__':
    
    sf6d = SimpleFull6DSpaceKnob()
    sf6d.loadFile(FILENAME)
    
    #ofs0 = [ (0,0,0), (0,0,0), (0,0,0), ]; ofs1 = [(0,0,0), (0,0,0), (0,0,0), ];
    #ofs0[0] = sf6d.estimateOffset(0)
    #ofs1[0] = sf6d.estimateCalibration(0)
    #sf6d.plotCalibration(0,ofs0[0])
    #sf6d.plotCalibration(0,ofs1[0])
    
    
#if 0==1:    
    sf6d.plotMagnetSignals(0)
    sf6d.plotMagnetSignals(1)
    sf6d.plotMagnetSignals(1)
    
    sf6d.printMagnetStats(0)
    sf6d.printMagnetStats(1)
    sf6d.printMagnetStats(2)
    
    sf6d.plotCalibration(0)
    sf6d.plotCalibration(1)
    sf6d.plotCalibration(2)
    
if 1==0:    
    ofs = [ (0,0,0), (0,0,0), (0,0,0) ]
    ofs[0] = sf6d.estimateOffset(0)
    ofs[1] = sf6d.estimateOffset(1)
    ofs[2] = sf6d.estimateOffset(2)
    sf6d.plotCalibration(0,ofs[0])
    sf6d.plotCalibration(1,ofs[1])
    sf6d.plotCalibration(2,ofs[2])

    for i in [0,1,2]: print('ofs: ',ofs[i])    
    
    
    
    #print( sf6d.findOffsets(0) )
    #print( sf6d.findOffsets(1) )
    #print( sf6d.findOffsets(2) )
    