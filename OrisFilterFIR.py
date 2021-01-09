# -*- coding: utf-8 -*-
#Digital Filter and File Conversion for Heart Sound
#Oris Project
#Author: Lucia Iannantuono

#**************************************************
#Import the required libraries

import numpy #numerical analysis library
import scipy #scientific library
from scipy import signal #signal analysis from scientific library

#**************************************************
def SignalQuality (data, fs):
    
    #Initialize variables
    quality = "not checked" #string of result to output to user
    sampling_freq = fs #sampling frequency passed to function
    flag = 0 #marker for detecting problems
    
    #Take absolute values of data
    data = abs(data)
    
    #Check the data for relatively extraneous peaks
    global_max = numpy.amax(data) #find the global max 
    rel_max = [] #create an empty list for storing relative peak indices
    rel_max_sum = 0 #initialize sum for average
    rel_max_num = 0 #initialize number of relative maxima
    j = 0 #initialize index variable
    for i in data: #for each data point
        if (i>(0.5*global_max)):#if amplitude is more than 50% of global max
            rel_max.append(j) #add index to list
        j=j+1 #increment index  
    no_duplicates = [] #create an empty list for the values after duplicates removed       
    for i in range (1,len(rel_max)): #go through list of values over half of global max
        if ((rel_max[i] - rel_max[i-1])<(int(sampling_freq*0.15))): #if less than 0.15s between points
            if(data[(rel_max[i])]>data[(rel_max[i-1])]): #if peak at i is bigger than i-1
                no_duplicates.append(rel_max[i]) #add peak at i to list
                rel_max_sum =  rel_max_sum + data[(rel_max[i])] #add magnitude of data to sum
                rel_max_num = rel_max_num + 1 #increment number of relative maxima
            else: #if peak at i is smaller than i-1  
                no_duplicates.append(rel_max[i-1]) #add peak at i to list
                rel_max_sum =  rel_max_sum + data[(rel_max[i-1])] #add magnitude of data to sum
                rel_max_num = rel_max_num + 1 #increment number of relative maxima
        else: #if spacing between points greater than 0.15s
            no_duplicates.append(rel_max[i]) #add peak at i to list               
    avg_rel_max = (rel_max_sum/max(rel_max_num,1)) #find average magnitude at maxima         
    rel_max = [] #empty the list of relative maxima
    j = 0 #re-initialize index variable
    for i in data: #loop through data points again
        if (i>(0.6*avg_rel_max)):#if amplitude is more than 60% of average relative max
            rel_max.append(j) #add index to list
        j=j+1 #increment index
    no_duplicates = [] #empty list for the values after duplicates removed       
    for i in range (1,len(rel_max)): #go through list of relative maxima again
        if ((rel_max[i] - rel_max[i-1])<(int(sampling_freq*0.15))): #less than 0.15s between points
            if(data[(rel_max[i])]>data[(rel_max[i-1])]): #if peak at i is bigger than i-1
                no_duplicates.append(rel_max[i]) #add peak at i to list 
            else: #if peak at i is smaller than i-1  
                no_duplicates.append(rel_max[i-1]) #add peak at i to list
        else: #if spacing between points greater than 0.15s
            no_duplicates.append(rel_max[i]) #add peak at i to list                     
    for i in range (1,len(no_duplicates)): #go through array with no duplicate entries
        if ((no_duplicates[i] - no_duplicates[i-1])>(int(sampling_freq*2.0))): #if more than 1.0s between points
            quality = "quiet interval detected: results may be inaccurate" #change message 
            flag = 1 #set flag to mark issue
    if ((avg_rel_max==0) or ((global_max/avg_rel_max)>1.9)): #if global max is more than 1.9 times the average
        quality = "high peak noise detected: results may be inaccurate" #change message 
        flag = 1 #set flag to mark issue
                                
    #If no issues detected, set quality result to good
    if(flag==0):
        quality = "good"        
                            
    return quality              
#**************************************************
def HeartRate (data, fs, ts, quality, S1_thresh, S2_thresh, fast_rate, beat_var, sample_var): 
    
    #Initialize variables
    heart_rate = 0.0 #heart rate of zero will be error indicator
    arrhythmia = "not checked" #set default arrhythmia message
    peak_widths = numpy.asarray([int(0.05*fs),int(0.08*fs), int(0.1*fs), int(0.15*fs)]) #set the acceptable peak widths
    all_beats = [] #create a list for all beats
    S1 = [] #create S1 list
    S2 = [] #create S2 list
    
    #Modify data for peak finding
    new_data = numpy.asarray(abs(data)) #take positive magnitude values
    for i in range(1,len(new_data)-1): #go through data to make it monotonic  
        if ((new_data[i-1]>new_data[i])and(new_data[i+1]>new_data[i])): #if local minima point
            new_data[i] = int(0.5*(new_data[i-1]+new_data[i+1]))#make the minimum equal to the average of values on either side
    new_data = signal.medfilt(new_data, 2*int(0.04*fs)+1) #apply median filter           
    new_data = numpy.power(new_data,1.3) #exponentiate the data
    new_data = signal.medfilt(new_data, 2*int(0.01*fs)+1) #apply median filter                       
    all_beats = findBeats(new_data, peak_widths, fs, S2_thresh) #get all beats   
    #Triage approach based on how fast heart rate seems to be
    if ((len(all_beats)*60/(2.0*ts)) > fast_rate): #if rough heart rate greater than fast threshold BPM
        S2_thresh = 0.5*S2_thresh #lower the S2 threshold
        all_beats = findBeats(new_data, peak_widths, fs, S2_thresh) #re-evaluate  beats    
    
    if (len(all_beats)>1): #if there are beats    
        #Call function to find the positions of S2 beats and add them to complete heartbeat list
        S1,S2 = categorizeBeats(new_data, all_beats, S1_thresh, S2_thresh, fs) 
                
        #Calculate nearest integer heart rate in BPM from prediction from number of all beats
        heart_rate = numpy.round(60.0*float(len(all_beats))/(2.0*ts)) 
            
        #Run function to check for arrhythmia in the sample
        arrhythmia = Arrhythmia (S1, S2, quality, beat_var, sample_var)
    
    #Return the heart rate value 
    return heart_rate, arrhythmia
    
#**************************************************
def findBeats (new_data, peak_widths, fs, S2_thresh):     
    
    #Initialize variables
    all_beats=[] #create empty list for beats
    peaks_to_remove = [] #create empty list for peaks that should be removed
    
    #Find all possible peaks and copy to list 
    all_peaks = scipy.signal.find_peaks_cwt(new_data, peak_widths, min_snr = 1.3) #locate potential peaks in data
    for i in all_peaks: #go through the final list of all peaks      
        all_beats.append(i) #copy value to beats list
        
    #Check magnitude of beats
    peaks_to_remove = [] #reset empty list of peaks to remove 
    beat_sum = 0.0 #numerator variable for average
    beat_num = 0.0 #denominator variable for average
    for i in range(0,len(all_beats)): #go through the potential returned peaks
        beat_num = beat_num + 1.0 #increment number of beats
        beat_sum = beat_sum + new_data[all_beats[i]] #add magnitude to sum of beats
    avg_beat_mag = beat_sum/max(beat_num, 1) #compute average beat magnitude  
    for i in range(0,len(all_beats)): #go through the potential returned peaks
        if ((new_data[all_beats[i]])<(S2_thresh*avg_beat_mag)): #if peak magnitude is less than minimum threshold
            peaks_to_remove.append(all_beats[i]) #put earlier index on list to be removed
    for i in peaks_to_remove: #go through the list of removals
        all_beats.remove(i) #remove item from list of all potential peaks  
        
    #Check for missed beats 
    peaks_to_add = [] #start with empty list of peaks to add
    for i in range(1,len(all_beats)): #go through the intervals between identified beats
        lower = all_beats[i-1] + int(0.15*fs) #set lower bound of interval
        upper = all_beats[i] - int(0.15*fs) #set lower bound of interval
        if(upper>lower): #if the spacing between beats is more than 0.3 seconds (200 bpm S1-S1 spacing)
            local_max_index = lower #initially set up local max index at lower end of interval
            for i in range(lower,upper+1): #go through the indices over the interval
                if(new_data[i]>new_data[local_max_index]): #if the magnitude at index i is greater than current local max
                    local_max_index = i #update the current local max
            if(new_data[local_max_index]>(S2_thresh*avg_beat_mag)): #if the magnitude of the local max in the interval is greater than the threshold 
                peaks_to_add.append(local_max_index) #add to the list of beats to add 
    final_upper = new_data[-1] #set upper bound for final interval
    if(final_upper>upper): #if the final interval is more than 0.15 seconds (200 bpm S1-S2 spacing)
            local_max_index = upper #initially set up local max index at lower end of interval
            for i in range(upper,final_upper+1): #go through the indices over the interval
                if(new_data[i]>new_data[local_max_index]): #if the magnitude at index i is greater than current local max
                    local_max_index = i #update the current local max
            if(new_data[local_max_index]>(S2_thresh*avg_beat_mag)): #if the magnitude of the local max in the interval is greater than the threshold 
                peaks_to_add.append(local_max_index) #add to the list of beats to add               
    for i in peaks_to_add: #go through the list of missed beats
        all_beats.append(i) #add to beats list
        
    #Check spacing between beats 
    peaks_to_remove = [] #reset empty list of peaks to remove
    all_beats.sort() #re-sort the list of beats after additions and removals    
    for i in range(1,len(all_beats)): #go through the potential returned peaks
        mag1 = new_data[(all_beats[i])] #find the magnitude of the peak at the current index
        mag0 = new_data[(all_beats[i-1])] #find the magnitude of the peak at the earlier index
        if ((all_beats[i]-all_beats[i-1])<int(0.15*fs)): #if spacing between peaks is less than 0.15 seconds (200 bpm, S1-S2 spacing)
            if (mag1>=mag0): #if current index has the bigger peak magnitude
                peaks_to_remove.append(all_beats[i-1]) #put earlier index on list to be removed
            else: #if earlier index has the bigger peak magnitude  
                peaks_to_remove.append(all_beats[i]) #put current index on list to be removed                    
    peaks_to_remove_in_removals = [] #empty list            
    for i in range (1,len(peaks_to_remove)): #go through the removal list
        if (peaks_to_remove[i-1]==peaks_to_remove[i]): #if there is a duplicate in the list to remove
            peaks_to_remove_in_removals.append(peaks_to_remove[i])
    for i in peaks_to_remove_in_removals: #go through the list of removals
        peaks_to_remove.remove(i) #remove duplicate items                          
    for i in peaks_to_remove: #go through the list of removals
        all_beats.remove(i) #remove item from list of all potential peaks 
        
    all_beats.sort() #ensure list is sorted      
                                                                                                                                                                                                                                              
    return all_beats
#**************************************************
def categorizeBeats (new_data, all_beats, S1_thresh, S2_thresh, fs): 
    S1 = []
    S2 = []
    
    #Categorize each beat as S1 or S2 based on its spacing
    for i in range(1,(len(all_beats)-1)): #go through the list of beats from the second item to the second last
        beat0 = all_beats[i-1] #set beat 0 at previous index
        beat1 = all_beats[i] #set beat 1 at current index
        beat2 = all_beats[i+1] #set beat 2 at next index
        
        if((beat1-beat0)<=(beat2-beat1)):#if beat 0 and beat 1 are closer together than beat 1 and beat 2
            if (i==1): #if the first position
                S1.append(beat0) #classify beat 0 as S1
                S2.append(beat1) #classify beat 1 as S2
            elif (i==(len(all_beats)-2)): #if last position
                S2.append(beat1) #classify beat 1 as S2 
                S1.append(beat2) #classify beat 2 as S1    
            else: #all other iterations
                S2.append(beat1) #classify beat 1 as S2     
        else:#if beat 0 and beat 1 are farther apart than beat 1 and beat 2 
            if (i==1): #if the first time through
                S1.append(beat1) #classify beat 1 as S1
                S2.append(beat0) #classify beat 0 as S2
            elif (i==(len(all_beats)-2)): #if last position
                S1.append(beat1) #classify beat 1 as S1 
                S2.append(beat2) #classify beat 2 as S2     
            else: #all other iterations
                S1.append(beat1) #classify beat 1 as S1
    
                
    #Find the average magnitude of S1 and S2 beats 
    S1_beat_sum = 0.0 #numerator variable for S1 average
    S1_beat_num = 0.0 #denominator variable for S1 average
    S2_beat_sum = 0.0 #numerator variable for S2 average
    S2_beat_num = 0.0 #denominator variable for S2 average    
    for i in range(0,len(S1)): #go through the S1 beats
        S1_beat_num = S1_beat_num + 1.0 #increment number of S1 beats
        S1_beat_sum = S1_beat_sum + new_data[all_beats[i]] #add magnitude to sum of S1 beats
    S1_avg_beat_mag = S1_beat_sum/max(S1_beat_num, 1) #compute average S1 beat magnitude  
    for i in range(0,len(S2)): #go through the S2 beats
        S2_beat_num = S2_beat_num + 1.0 #increment number of S2 beats
        S2_beat_sum = S2_beat_sum + new_data[all_beats[i]] #add magnitude to sum of S2 beats
    S2_avg_beat_mag = S2_beat_sum/max(S2_beat_num, 1) #compute average S2 beat magnitude                       
                                                    
    #Go back through S1 list to see if there are any two without an S2 between
    S1_removals = [] #create empty list for S1 removals
    S2_additions = [] #create empty list for S2 additions
    for i in range(1,len(S1)): #go through all positions in S1
        beat0 = S1[i-1] #previous S1 beat
        beat1 = S1[i] #current S1 beat
        double_S1 = True #default set double beat of S1 as true
        for j in S2: #go through each S2 element
            if ((j>beat0) and (j<beat1)): #if the S2 element falls between the two S1 beats
                double_S1 = False #set the double flag to false
        mag0 = new_data[beat0] #find the magnitude of beat 0
        mag1 = new_data[beat1] #find the magnitude of beat 1        
        if((double_S1==True)and((mag1<S1_avg_beat_mag*S1_thresh)or(mag0<S1_avg_beat_mag*S1_thresh))): #if there was no S2 between beat0 and beat1, and either is less than the S1 threshold
            if (mag1>=mag0): #if beat1 bigger
                S1_removals.append(beat0) #beat0 to be removed from S1    
                S2_additions.append(beat0) #beat0 to be reassigned as S2
            else: #if beat0 bigger  
                S1_removals.append(beat1) #beat1 to be removed from S1    
                S2_additions.append(beat1) #beat1 to be reassigned as S2
    S1_removals.sort() #sort the list of S1 removals                
    S1_removal_duplicates = [] #create empty list for duplicates in removal list
    for i in range(1,len(S1_removals)): #loop through indices
        if (S1_removals[i]==S1_removals[i-1]): #if there is a duplicate
            S1_removal_duplicates.append(S1_removals[i-1]) #put that value in the duplicates list
    for i in  S1_removal_duplicates: #for each duplicate
        S1_removals.remove(i) #remove from removals list
    S1_removals.sort() #sort the list of S2 removals                  
    for i in S1_removals: #go through removal list
        S1.remove(i) #remove values from S1 list
    for i in S2_additions: #go through addition list    
        S2.append(i) #add values to S2 list
    S1.sort() #re-sort S1
    S2.sort() #re-sort S2 
    
    
    #Go back through S2 list to see if there are any two without an S1 between
    S2_removals = [] #create empty list for S2 removals
    S1_additions = [] #create empty list for S1 additions
    for i in range(1,len(S2)): #go through all positions in S2
        beat0 = S2[i-1] #previous S2 beat
        beat1 = S2[i] #current S2 beat
        double_S2 = True #default set double beat of S2 as true
        for j in S1: #go through each S1 element
            if ((j>beat0) and (j<beat1)): #if the S1 element falls between the two S2 beats
                double_S2 = False #set the double flag to false
        if((double_S2==True)and((beat1-beat0)<int(0.6*fs))): #if there was no S2 between beat0 and beat1, and the spacing is less than 0.6 sec
            mag0 = new_data[beat0] #find the magnitude of beat 0
            mag1 = new_data[beat1] #find the magnitude of beat 1
            if (((mag0<S2_avg_beat_mag)or(mag1<S2_avg_beat_mag))and((mag0<S1_thresh*S1_avg_beat_mag)or(mag1<S1_thresh*S1_avg_beat_mag))): #if either is very small, and both are not S1, likely not an S2
                if (mag1>=mag0): #if beat1 bigger
                    S2_removals.append(beat0) #remove beat0
                else: #if beat0 bigger
                    S2_removals.append(beat1) #remove beat1
            else: #both beats adequately large             
                if (mag1>=mag0): #if beat1 bigger
                    S2_removals.append(beat0) #beat0 to be removed from S2 
                    if (mag0>0.5*S1_thresh*S1_avg_beat_mag):  #if large enough, at least 50% of regular threshold value
                        S1_additions.append(beat0) #beat0 to be reassigned as S1 
                else: #if beat0 bigger, 
                    S2_removals.append(beat1) #beat1 to be removed from S2 
                    if (mag1>0.5*S1_thresh*S1_avg_beat_mag):  #if large enough, at least 50% of regular threshold value  
                        S1_additions.append(beat1) #beat1 to be reassigned as S1
    S2_removals.sort() #sort the list of S2 removals                
    S2_removal_duplicates = [] #create empty list for duplicates in removal list
    for i in range(1,len(S2_removals)): #loop through indices
        if (S2_removals[i]==S2_removals[i-1]): #if there is a duplicate
            S2_removal_duplicates.append(S2_removals[i-1]) #put that value in the duplicates list
    for i in  S2_removal_duplicates: #for each duplicate
        S2_removals.remove(i) #remove from removals list
    S2_removals.sort() #sort the list of S2 removals                    
    for i in S2_removals: #go through removal list
        S2.remove(i) #remove values from S2 list
    for i in S1_additions: #go through addition list    
        S1.append(i) #add values to S1 list
    S1.sort() #re-sort S1
    S2.sort() #re-sort S2              
                                                                                                                                                                                                                                       
    return S1,S2 
#**************************************************
def Arrhythmia (S1, S2, quality, beat_var, sample_var): 
    
    #Initialize parameters
    variation_thresh = beat_var #ratio of difference between two beats that is considered arrhythmic 
    arrythmia_thresh = sample_var #fraction of arrhythmic hearbeats in the sample to suggest arrhythmia
    
    #Look for arrhythmia    
    if ((quality == "good")and(len(S1)>1)):#if quality is good
        arrhythmia = "no arrhythmia detected" #default message status is good
        
        #Find average S1 spacing
        S1_num = 0 #initialize number of intervals to zero
        S1_sum = 0 #initialize sum of spacing to zero
        for i in range(1,len(S1)): #loop through all elements in list
            S1_sum = S1_sum + (S1[i]-S1[i-1]) #add space from element to preceeding element
            S1_num = S1_num + 1 #increment number of intervals
        S1_avg_space = S1_sum/max(S1_num,1) #compute average spacing
        
        #Find average S2 spacing
        S2_num = 0 #initialize number of intervals to zero
        S2_sum = 0 #initialize sum of spacing to zero
        for i in range(1,len(S2)): #loop through all elements in list
            S2_sum = S2_sum + (S2[i]-S2[i-1]) #add space from element to preceeding element
            S2_num = S2_num + 1 #increment number of intervals
        S2_avg_space = S2_sum/max(S2_num,1) #compute average spacing
        
        #Count number of S1 beats with spacing anomalies greater than max acceptable variation
        S1_vars = 0 #initialize variable beat counter to zero
        for i in  range(1,len(S1)): #loop through list
            if ((abs((S1[i]-S1[i-1]-S1_avg_space)/S1_avg_space))>variation_thresh): #if relative space error above variability threshold
                S1_vars = S1_vars + 1 #add to count
        
        #Count number of S2 beats with spacing anomalies greater than max acceptable variation
        S2_vars = 0 #initialize variable beat counter to zero
        for i in  range(1,len(S2)): #loop through list
            if ((abs((S2[i]-S2[i-1]-S2_avg_space)/S2_avg_space))>variation_thresh): #if relative space error above variability threshold
                S2_vars = S2_vars + 1 #add to count 
         
        #If too high a proportion of variable beats, flag arrhythmia
        if ((S1_vars/(len(S1)-1))>arrythmia_thresh): #if too many arrythmic S1 beats
            arrhythmia = "arrhythmia detected (S1)" #display S1 arrhythmia message
        if ((S2_vars/(len(S2)-1))>arrythmia_thresh): #if too many arrythmic S1 beats
            if (arrhythmia == "S1"): #if S1 already flagged as arrhythmic
                arrhythmia == "arrhythmia detected (S1 and S2)" #display S1 and S2 arrhythmia message
            else: #if only S2 flagged as arrhythmic
                arrhythmia == "arrhythmia detected (S2)" #display S2 arrhythmia message         
     
    #Indicate unable to look for arrhythmia
    else: #if quality is not good
        arrhythmia = "signal quality not sufficient for diagnosis"    
            
    return arrhythmia
#**************************************************
def OrisFilterFIR (recording, low, high, freq_shift, S1_beat_thresh, S2_beat_thresh, fast_rate, beat_var, sample_var, processing_enable):

    #Format the data for filtering
    sample_time = float(recording[-1]) #last of text file line gives run time
    data = numpy.ndarray(shape=(recording.size-1,),dtype= 'float32') #create new array for removing the last entry
    j = 0 #tracking variable for index of input data array
    for i in (numpy.ones(shape =(recording.size-1,))): #for all but the last element
        data[j] = recording[j] #copy the data
        j=j+1 #increment index   
    num_samples = data.size #find the number of samples 
    sampling_freq = num_samples/sample_time #compute sampling frequency
    sound = numpy.ndarray(shape=(data.size,),dtype= 'float32') #create new array for the detrended sound values
    det = signal.detrend(data, type = 'constant') #detrend the median from the sound signal
    dataMax = max(numpy.amax(det), abs(numpy.amin(det))) #find the scaling factor of the detrended data points
    j=0 #re-use looping index variable
    for i in det: #go through the original data array
        sound[j] = i* (1/float(dataMax)) #center data around middle and scale so that mag <=1  
        j=j+1 #increment index       
    
    #Check quality of filtered signal
    quality = SignalQuality(sound, sampling_freq)
           
    #Set up the FIR bandpass filter 
    pass_low = low #set lower frequency of passband
    pass_high = high #set upper frequency of passband
    
    #Create the bandpass filter based on the calculated parameters 
    FIR_filt = signal.firwin(401, [pass_low, pass_high], nyq = sampling_freq/2, pass_zero=False)
    
    #Create bandstop filter based on the typical ambient noise frequencies
    FIR_noisefilt = signal.firwin(401, [35, 38, 59, 65], nyq = sampling_freq/2)

    #Perform digital filtering by applying the filters
    filtered = signal.lfilter(FIR_filt, 1.0, sound)
    filtered = signal.lfilter(FIR_noisefilt, 1.0, filtered)

    #Re-scale after digital filtering
    filteredSound = numpy.ndarray(shape=(filtered.size,),dtype= 'float32') #create new array for the scaled filtered values
    filteredMax = numpy.amax(filtered) #find the new max data point
    filteredMin = numpy.amin(filtered) #find the new min data point
    scaleFactor = 1/(max(filteredMax, abs(filteredMin))) #scale for max magnitude of 1
    j=0 #re-use looping index variable
    for i in filtered: #go through the filtered array
        filteredSound[j]= i*scaleFactor #scale to be in range [-1, 1]
        j=j+1 #increment index
    
    #Find the heart rate of the sample and check for arrhythmia
    if ((quality=="good")and (processing_enable==True)): #if quality is good and processing is enabled
        heart_rate, arrhythmia = HeartRate(filteredSound, sampling_freq, sample_time, quality, S1_beat_thresh, S2_beat_thresh, fast_rate, beat_var, sample_var)
    else: #if quality is not good or processing not enabled
        heart_rate = 0 #error heart rate is zero
        arrhythmia = "not run" #error arrhythmia message 
    
    #Perform freq analysis and shift for playback 
    filt_spectrum = numpy.fft.rfft(filtered) #find frequency spectrum of filtered sound 
    filt_shift = numpy.ndarray(shape = filt_spectrum.size, dtype = complex) #create array for shifted frequency
    for i in range(0, filt_spectrum.size-1): #loop through shifted array
        shift = 10*freq_shift #compute amount to shift by
        if (i<shift):
            filt_shift[i] = 0 #pad beginning with zeros
        else:    
            filt_shift[i] = filt_spectrum[i-shift] #copy with index offset by shift  
    shiftedSound = numpy.fft.irfft(filt_shift) #perform inverse FFT to get shifted sound
    
    #Re-scale shifted sound
    shiftedMax = numpy.amax(shiftedSound) #find the new max data point
    shiftedMin = numpy.amin(shiftedSound) #find the new min data point
    scaleFactor = 1/(max(shiftedMax, abs(shiftedMin))) #scale for max magnitude of 1
    j=0 #re-use looping index variable
    for i in shiftedSound: #go through the filtered array
        shiftedSound[j]= i*scaleFactor #scale to be in range [-1, 1]
        j=j+1 #increment index

    #Change the data type to int16 for analysis
    #change the data type for the raw sound
    sound_int16 = numpy.ndarray(shape=(sound.size,),dtype= 'int16') #create new array for the unfiltered sound file
    j=0 #re-use looping index variable
    for i in sound: #go through the raw audio with the [-1, 1] range 
        sound_int16[j] = min(i,1)*32767 #copy for values ranged [0, 255]
        j=j+1 #increment index
    #change the data type for the filtered sound    
    filteredSound_int16 = numpy.ndarray(shape=(filteredSound.size,),dtype= 'int16') #create new array for the filtered sound file
    j=0 #re-use looping index variable
    for i in filteredSound: #go through the filtered audio with the [-1, 1] range
        filteredSound_int16[j] = min(i,1)*32767 #copy for values ranged [0, 255]
        j=j+1 #increment index  
    #change the data type for the filtered shifted sound    
    shiftedSound_int16 = numpy.ndarray(shape=(shiftedSound.size,),dtype= 'int16') #create new array for the filtered sound file
    j=0 #re-use looping index variable
    for i in shiftedSound: #go through the filtered audio with the [-1, 1] range
        shiftedSound_int16[j] = min(i,1)*32767 #copy for values ranged [0, 255]
        j=j+1 #increment index 
            
    #Output the sampling freq, sound array, and filtered array     
    return sampling_freq, quality, heart_rate, arrhythmia, sound_int16, shiftedSound_int16

#**************************************************        
