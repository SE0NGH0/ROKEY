def update(mean1, var1, mean2, var2):
    new_mean = float(var2 * mean1 + var1 * mean2) / (var1 + var2)
    new_var = 1./(1./var1 + 1./var2)
    return [new_mean, new_var]

def predict(mean1, var1, mean2, var2):
    new_mean = mean1 + mean2
    new_var = var1 + var2
    return [new_mean, new_var]

measurements = [5., 6., 7., 9., 10.]  # means of measurement
motion = [1., 1., 2., 1., 1.]  # means of motion
measurement_sig = 4.  # uncertainties of both measurement(update) and motion(predict) remain same
motion_sig = 2.
mu = 0.
sig = 10000.

#Please print out ONLY the final values of the mean
#and the variance in a list [mu, sig]. 
# Insert code here
for k in range(len(measurements)):
    mu, sig = update(mu, sig, measurements[k], measurement_sig)
    mu, sig = predict(mu, sig, motion[k], motion_sig)

print ([mu, sig]) # mean and variance of the posterior belief (next position and its variance)