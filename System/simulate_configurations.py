# -*- coding: utf-8 -*-
"""
Created on Mon Oct  9 18:28:00 2023

@author:   BastelBaus
@content:  Script to simulate and evaluate different settings 
           of the SimpleFull6DSpaceKnob.
"""


import magpylib as magpy
import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial.transform import Rotation as R

# geometric parameters
z0         = 15      # [mm] distance between magnets and sensors
r_mag      = 15      # [mm] circle around which magnets are placed in 120° spacing
r_sen      = 15      # [mm] circle around which 3D sensors are placed in 120° spacing
mag_rot = 58*0;        # [°] rotation of magnets relative to sensors
mag_dia = 5          # [mm] diameter of magnet

# simulation parameters
n        = 100;     # number of points foir each segment
rot_span = 5;        # [°] full span of rotation
mov_span = 2;        # [mm] full span of linear movement 


# properties of magnetic sensor
mag_noise  = 0.0001  # [mT] 
mag_sens_low  =  3000 # [LSB/G] Sensitivity of magnetometer
mag_sens_high = 12000 # [LSB/G] Sensitivity of magnetometer
mag_sens = mag_sens_high 
mag_sens_mT = mag_sens/10 # [LSB/mT] convert GAUSS to TEslas: 1G = 10-4T ==> 1G = 10mT

# flags to configure simulation
show_animation    = False
show_fit_result   = False
show_setup        = False
show_measurements = False;


def main():
    
    # Create a Cuboid magnet with magnetic polarization
    # of 1000 mT pointing in x-direction and sides of
    # 1,2 and 3 mm respectively.    
    #cube = magpy.magnet.Cuboid(magnetization=(1000,0,0), dimension=(1,2,6))    
    #ts = np.linspace(0, 60, 60)
    #pos = np.array([(40, 40, np.sin(2*np.pi*t/30)*4) for t in ts])    
    #pos = np.array([(np.sin(2*np.pi*t/30)*4, np.cos(2*np.pi*t/30)*4, 0) for t in ts])

    
    
    # the default positions of the magnets 
    pos1 = (np.sin(np.deg2rad(   0))*r_mag, np.cos(np.deg2rad(   0))*r_mag, 0)
    pos2 = (np.sin(np.deg2rad( 120))*r_mag, np.cos(np.deg2rad( 120))*r_mag, 0)
    pos3 = (np.sin(np.deg2rad(-120))*r_mag, np.cos(np.deg2rad(-120))*r_mag, 0)
    ori1 = R.from_rotvec((0, 0, 0))
    ori2 = R.from_rotvec((0.5*np.pi, 0, 0))
    ori3 = R.from_rotvec((0, 0.5*np.pi, 0))
    #ori1 = ori2; ori3 = ori1
    #ori2 = ori1; ori3 = ori1
    mag_size     = (mag_dia,1.7)
    mag_strength = (0,0,1000)
    
    cube1 = magpy.magnet.Cylinder(magnetization=mag_strength, dimension=mag_size, position=pos1, orientation=ori1 )
    cube2 = magpy.magnet.Cylinder(magnetization=mag_strength, dimension=mag_size, position=pos2, orientation=ori2 )
    cube3 = magpy.magnet.Cylinder(magnetization=mag_strength, dimension=mag_size, position=pos3, orientation=ori3 )
    cube1.rotate_from_angax(mag_rot, "z", anchor=0, start=0)
    cube2.rotate_from_angax(mag_rot, "z", anchor=0, start=0)
    cube3.rotate_from_angax(mag_rot, "z", anchor=0, start=0)
    cubes = magpy.Collection(cube1,cube2,cube3)    
    
    # Create a Sensor for measuring the field
    pos1 = (np.sin(np.deg2rad(   0))*r_sen, np.cos(np.deg2rad(   0))*r_sen, -z0)
    pos2 = (np.sin(np.deg2rad( 120))*r_sen, np.cos(np.deg2rad( 120))*r_sen, -z0)
    pos3 = (np.sin(np.deg2rad(-120))*r_sen, np.cos(np.deg2rad(-120))*r_sen, -z0)
    
    sensor1 = magpy.Sensor(position=pos1)
    sensor2 = magpy.Sensor(position=pos2)
    sensor3 = magpy.Sensor(position=pos3)    
    sensor1.rotate_from_angax(angle=   0, axis='z') # vectors perpendicular to center
    sensor2.rotate_from_angax(angle=-120, axis='z') # vectors perpendicular to center
    sensor3.rotate_from_angax(angle=+120, axis='z') # vectors perpendicular to center
    sensors = magpy.Collection(sensor1,sensor2,sensor3)

    
    

    # vectrors for rotation, movement and nothing
    r = np.linspace(-rot_span, rot_span, n); # rotation vector r
    m = np.linspace(-mov_span , mov_span , n); # movement vector m
    z = np.zeros(n); # zero vector z
    
    # rotations in each axis
    rot1 = np.concatenate((r,z,z,z,z,z));
    rot2 = np.concatenate((z,r,z,z,z,z));
    rot3 = np.concatenate((z,z,r,z,z,z));
    rot  = np.transpose( np.concatenate([[rot1],[rot2],[rot3]]));
    cubes.rotate_from_angax(rot1, "x", anchor=0, start=0)
    cubes.rotate_from_angax(rot2, "y", anchor=0, start=0)
    cubes.rotate_from_angax(rot3, "z", anchor=0, start=0)
    
    # movements in each direction
    mov1 = np.concatenate((z,z,z,m,z,z));
    mov2 = np.concatenate((z,z,z,z,m,z));
    mov3 = np.concatenate((z,z,z,z,z,m));
    mov = np.transpose([mov1, mov2 ,mov3])
    cubes.move(mov, start=0)

    # the matrix of displacemenbt of the knob in all 6 dimensions
    displacement = np.concatenate([rot,mov],axis=1)
       

    # measrured B field and transformed with arctan
    Bm = magpy.getB(cubes, sensors).reshape(6*n,9) + np.random.randn(6*n,9)*mag_noise    
    Bm = np.round(Bm*mag_sens)/mag_sens; # resolution    
    Bx = np.arctan(Bm);
    B  = np.concatenate([Bm,Bx],axis=1)
    
    
    # regress and estimate
    reg = np.linalg.lstsq(B,displacement)[0]
    estimated = np.matmul(B,reg)    
    rms = np.sqrt(np.mean(np.square(estimated-displacement)));
    #np.set_printoptions(formatter={'float': "\t{: 5.1f}\t".format})
    #print(reg)
    #print(rms)
    
    # show results

    if show_measurements:
        for i in range(9):
            plt.plot(Bm[:,i])
        plt.title('Raw measurements')
        plt.ylabel('field [mT]');
        plt.show();
        
        for i in range(9):
            plt.plot(Bm[:,i]-np.mean(Bm[:,i]))
        plt.title('Raw measurements')
        plt.ylabel('field [mT]');
        plt.show();
            

    if show_fit_result:
        plt.subplot(2,1,1)
        for i in range(6): plt.plot(estimated[:,i])
        plt.title('Least Square Fit Results')
        plt.ylabel('estim. displ.[°] and [mm]');
        plt.subplot(2,1,2)
        for i in range(6): plt.plot(displacement[:,i])
        plt.ylabel('real displ.[°] and [mm]');plt.xlabel('simulation step')
        plt.show()
        
    if show_setup:
        magpy.show(cubes, sensors, backend='matplotlib')
    
    if show_animation:
        with magpy.show_context(cubes, sensors, animation=True, backend='matplotlib'):
            magpy.show(col=1)
            magpy.show(output='Bx',col=2, style_legend_show=False )
            magpy.show(output='By',col=3, style_legend_show=False )
            magpy.show(output='Bz',col=4, style_legend_show=False )
    
    
    return rms;

if __name__ == '__main__':

    if 1==1:
        show_fit_result = True
        show_setup      = True
        show_measurements = True;
        print(main())
    

    if 1==2: # find optimal mag dia
        show_fit_result = False
        show_setup      = False
        show_measurements = False;
            
        d = np.zeros(120)
        for i,mag_dia in enumerate(range(120)):
            print(i,' of ', 120 )
            mag_dia = mag_dia/120*4+3
            d[i] = main()
        plt.plot(np.array(range(120))/120*4+3,d)
        plt.xlabel('mag diameter [mm]'); plt.ylabel('rms error')
        plt.ylim(0,0.05);
        plt.show()
        mag_dia = 5;
        
    if 1==2: # find optimal displacement
        show_fit_result = False
        show_setup      = False
        show_measurements = False;
        
            
        d = np.zeros(3600)
        for i,mag_rot in enumerate(range(3600)):
            print(i,' of ', 3600 )
            mag_rot = mag_rot/10
            d[i] = main()
        plt.plot(np.array(range(3600))/10,d)
        plt.xlabel('mag rotation [°]'); plt.ylabel('rms error')
        plt.ylim(0,0.05);
        plt.show()
        mag_rot = 58;

    if 1==2: # find optimal displacement
        show_fit_result = False
        show_setup      = False

        d = np.zeros((25,15))
        for k, r_mag in enumerate(range(25)):
         for l,r_sen in enumerate(range(15)):
            a = main();
            print(r_mag,' / ', r_sen, ' = ', a )            
            d[k,l] = a
        
        d[d>0.3] = None
        xpos, ypos = np.meshgrid(range(25),range(15), indexing="ij")
        fig = plt.figure()
        ax = fig.add_subplot(projection='3d')
        ax.plot_surface(xpos, ypos, d, edgecolor='royalblue', lw=0.5, rstride=1, cstride=1, alpha=0.3)
        ax.set_zlim(0,0.2)
        plt.xlabel('r_magnet  [mm]'); plt.ylabel('r_sensor [mm]'); ax.set_zlabel('rms error')
        plt.show()

        r_mag = r_sen = 15;