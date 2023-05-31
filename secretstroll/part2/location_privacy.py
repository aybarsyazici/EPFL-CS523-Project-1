import numpy as np
from scipy.special import lambertw
from geopy.distance import EARTH_RADIUS

## Grid parameters
MAP_LAT = 46.5
MAP_LON = 6.55

MAP_SIZE_LAT = 0.07
MAP_SIZE_LON = 0.10

def is_acceptable(location: tuple):
    # verify whether location is valid or not 
    #(in this case, accordingly to the dataset map boundaries)
    lat = location[0]
    lon = location[1]
    return (lat>=MAP_LAT and lat<=MAP_LAT+MAP_SIZE_LAT) and lon>=MAP_LON and lon<=MAP_LON+MAP_SIZE_LON

def draw_laplacian_noise(eps):
    theta =  np.random.uniform(low=0,high=2*np.pi)
    p = np.random.uniform(low=0,high=1)
    r = (-1/eps)*(lambertw((p-1)/(np.exp(1)),k=-1,tol=1e-8).real+1)
    return theta, r



def get_obfuscated_location(x,epsilon):
    while True:
        theta, r = draw_laplacian_noise(epsilon)

        lat,lon=np.deg2rad(x[0]),np.deg2rad(x[1])
        r_ang=r/EARTH_RADIUS
        noisy_lat = np.arcsin(np.sin(lat)*np.cos(r_ang)+np.cos(lat)*np.sin(r_ang)*np.cos(theta))
        noisy_lon = lon + np.arctan2(np.sin(theta)*np.sin(r_ang)*np.cos(lat),np.cos(r_ang)-np.sin(lat)*np.sin(noisy_lat))
        noisy_lon = (noisy_lon + 3 * np.pi) % (2 * np.pi) - np.pi;

        z=(np.rad2deg(noisy_lat),np.rad2deg(noisy_lon))
        if is_acceptable(z):
            return z
        
