def find_start_and_end_helper(xf, threshold = 2000): 
    import numpy as np    
    start_idx = -1
 
    for k in range(0, len(xf)):
        if(np.abs(xf[k])) > threshold:
            start_idx = k
            break

    if(start_idx  < 0):
        print "Unable to detect start of transmission"
        return -1
    
    end_idx = -1
    
    for k in range(0, len(xf)):
        if(np.abs(xf[len(xf)-k-1])) > threshold:
            end_idx = len(xf)-k-1
            break

    if(end_idx < 0):
        print "Unable to detect end of transmission"
        return -1

    return start_idx, end_idx



def decode_bits(xf, threshold = 2000, symbol_len = 250 ):
    import numpy as np
    start_idx, end_idx = find_start_and_end_helper(xf, threshold)   
    
    if((start_idx < 0) or (end_idx < 0)):
        return -1
     
    bits = np.sign(xf[start_idx+np.ceil(symbol_len/2):end_idx:symbol_len])
    bits = bits*bits[0]
    bits = (bits[1:] + 1.0)/2
    return bits





def generate_bpsk_signal(bits, rate=8000, symbol_len = 250, freq = 1000):

    import numpy as np

    num_symbols = len(bits)

    sound_len = ((num_symbols+3.0)*symbol_len/rate)
   
    ts = np.arange(0, sound_len, 1/float(rate))

    c = np.cos(2*np.pi*freq*ts)*(2**13)
    preamble = np.append(np.zeros(symbol_len), np.ones(symbol_len))
    Pulse = np.ones(symbol_len)

    dat = 2*bits
    dat = dat-np.ones(len(dat))

    m = preamble

    for k in range(0, len(dat)): 
        m = np.append(m, dat[k]*Pulse)

    # pad the end with zeros
    postamble = np.zeros(len(ts)-len(m))
    m = np.append(m, postamble)

    # modulate the signal
    x = c*m

    return x



def decode_bpsk_signal(x, freq=1000, rate = 8000, symbol_len = 250, detection_threshold_factor = 0.3, LPFbw = 320):

    import numpy as np
    ts = np.arange(0,(len(x)/float(rate)), 1/float(rate))

    threshold = detection_threshold_factor*np.max(x)

    start_index, end_index =  find_start_and_end_helper(x, threshold)

    x = x[start_index:end_index]

    ts = ts[0:len(x)]

    Ts = ts[1]-ts[0]
    Wc = LPFbw
    # this is the impulse response of our filter
    ts_filt =  np.arange(-symbol_len*2.0/rate,symbol_len*2.0/rate, 1/float(rate))
    filt = np.sinc(ts_filt/np.pi*Wc)

    max_var = -1

    for phi in np.linspace(-np.pi, np.pi, 16):
        c = np.cos(2*np.pi*freq*ts+phi)
        xc = x*c
        # convolve with the impulse response of our filter
        xf = np.convolve(xc, filt)
        cur_var = np.var(xf[0:len(x)/2])
        if(max_var < cur_var):
            best_phi = phi
            max_var = cur_var

    c = np.cos(2*np.pi*freq*ts+best_phi)
    xc = x*c
    # convolve with the impulse response of our filter
    xf = np.convolve(xc, filt)


    threshold = detection_threshold_factor*np.max(xf)
    bits = decode_bits(xf,threshold,symbol_len)    
    
    return bits
 


def help():

    print "This module provides:"
    print ""
    print "     generate_bpsk_signal(bits, rate=8000, symbol_len = 250, freq = 1000):"
    print "         Returns a numpy array which is a BPSK encoding of bits"
    print "         1 symbol worth of zeros are added at the beginning and the end to aid detection of transmission start"
    print "         A 1 bit is added to the beginning to help with synchronization"
    print "         bits -  a numpy array of 1s and 0s"
    print "         rate - sample rate used"
    print "         symbol_len - length in samples of the rectangular pulse used to encode the bits"
    print "         freq - carrier frequency in Hz"
    print ""
    print "     decode_bpsk_signal(x, freq=1000, rate = 8000, symbol_len = 250, detection_threshold_factor = 0.3, LPFbw = 320):"
    print "         Decodes a received BPSK signal in vector x and produces a numpyarray of bits "
    print "         The function uses a brute-force approach to carrier phase synchronization by checking 16 evenly spaced"
    print "         phase offsets between -pi and pi to find the one which results in the strongest demodulated signal"
    print "         which is then used as the demodulated signal"
    print "         The first bit is assumed to be a control bit that always equals 1. This bit is not returned in the final output"
    print "         x - a numpy array of the received audio samples"
    print "         freq - carrier frequency "
    print "         rate - sample rate used "
    print "         symbol_len - length in samples of the rectangular pulse"
    print "         detection_threshold_factor - this is used for detecting the start and end of transmission"
    print "                                      the start of transmission is the first sample that exceeds"
    print "                                      detection_threshold_factor times the maximum value in x"
    print "                                      the end of transmission is the last sample that exceeds"
    print "                                      detection_threshold_factor times the maximum value in x"
    print "         LPFbw - this is the bandwidth in rad/sec of the low-pass filter that is used after"
    print "                 multiplying with a cosine"                 
