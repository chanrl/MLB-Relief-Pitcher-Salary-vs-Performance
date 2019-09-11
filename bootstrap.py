import numpy as np
import scipy.stats as stats
import matplotlib.pyplot as plt

def bootstrap(x, resamples=10000):
    """Draw bootstrap resamples from the array x.

    Parameters
    ----------
    x: np.array, shape (n, )
      The data to draw the bootstrap samples from.
    
    resamples: int
      The number of bootstrap samples to draw from x.
    
    Returns
    -------
    bootstrap_samples: List[np.array]
      The bootsrap resamples from x.  
      Each array is a single bootstrap sample.
    """
    n_obs = x.shape[0]
    boot_samples = []
    for k in range(resamples):
        boot_idxs = np.random.randint(n_obs, size=n_obs)
        boot_sample = x[boot_idxs]
        boot_samples.append(boot_sample)
    return boot_samples

# fig, ax = plt.subplots(figsize=(10, 4))

# ax.hist(, bins=20)
# ax.set_ylabel('Count')
# ax.set_xlabel('Means')

# corr, p_value = stats.pearsonr(col_A, salary)
# print(f"The correlation is: {corr:2.2f}")

# lower_ci, upper_ci, bootstrap_corr_law = bootstrap_confidence_interval(
#     law_sample, 
#     stat_function=lambda x: stats.pearsonr(x[:, 0], x[:, 1])[0],
#     resamples=10000, ci=95)
# print("Bootstrapped 95% CI of Law school correlation coeff: ({:2.2f}, {:2.2f})".format(lower_ci, upper_ci))
# print("Bootstrapped 95% CI does not contain 0, so LSAT seems predictive of GPA")

# plt.hist(bootstrap_corr_law)
# plt.xlabel('Correlation Coeff.')
# plt.ylabel('Count')

# law_all = np.loadtxt('law_all.txt')
# corr_coeff, p_val = stats.pearsonr(law_all[:, 0], law_all[:, 1])
# print("Population-wide LSAT and GPA correlation and P-value: {:2.2f}".format(corr_coeff))