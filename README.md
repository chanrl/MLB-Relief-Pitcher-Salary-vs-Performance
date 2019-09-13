# MLB Relief Pitcher Salary vs Performance

## Glossary

* Background
* Objectives
* Hypothesis
* Conclusions

## Background

MLB Relief pitcher salary vs performance

This capstone project pulled MLB relief pitcher salary and stats from the Baseball-Reference website in order to determine if there is a positive trend with pitcher salaries and their performance.

In the MLB season of 2019, it appears from a spectator's point of view that many highly paid relief pitchers who have signed a large contract are performing worse than expectations. 

If a GM decides to sign a relief pitcher to a large contract, you would assume that the relief pitcher would be elite or better than an average pitcher. Thus, a relief pitcher with a higher salary should have better performance versus one with a lower salary.

This project will visualize and attempt to identify trends in relief pitcher performances and their salary.

## Objectives

* Scrape web data from baseball-reference to be used in pandas
* Clean and prepare data for statistical tests and visualizations
* Run statistical tests and gather results
* Analyze results and observations, create visualizations of results

## Hypothesis

Null Hypothesis: There is no difference in performance for relief pitchers who are paid more than those that are paid less.

Alternative Hypothesis: Relief pitchers that are signed to a large contract perform differently than those with smaller contracts.

Significance level = .05

## Conclusion

On the performance metrics of RA9 (runs allowed per 9 innings), RAA (runs allowed above average), RAR (runs allowed above replacement), WAA (wins above average), and WAR (wins above replacement),
higher paid relief pitchers do perform better than lower paid relief pitchers in 2019 as well as the sum of all pitchers from 2015 - 2019. The difference has a higher significance when separating 
by the top 20th percentile versus the top 30th percentile of pitcher salaries. The difference in means is not a measure of the exact value of how much better the group of higher paid pitchers
are versus the lower paid group, but it shows that they do perform better. To quantify how much better the higher paid group versus the lower paid group and the value of salary is something else
worth investigating.

This was reinforced by bootstrapping the samples from 2019, as well as the sum of the all samples from 2019-2015. The bootstrapped sample distributions are able to show that the higher
paid group of pitchers have a better performance if observing the mean of their distribution.

An interesting point to note is that for the group of pitchers in 2019, there are some means in the distribution inside the 95% confidence interval that falls below 0 for the performance metric of RAA. 
RAA is how many runs allowed a pitcher is better than an average pitcher in the league. This shows that for this group, it is possible that if this season was played again over an x amount of simulations,
it is possible to observe this group of highly paid pitchers performing worse than the league average.

The correlation between salary and pitcher performance was also tested. The p-values for the pearson correlation coefficients found were above the .05 significance level.
The data was not able to prove that there was a correlation between relief pitcher salaries and their performances. Another interesting point is if we accept the significance level as .10,
for the pitchers in 2019 split by the top 20% of pay, the higher paid group has a negative correlation coefficient and the lower paid group has a positive correlation coefficient,
indicating the the higher paid group performed worse as their salary increased and vice versa.

Lastly, the correlation between salary and pitcher performance as a sum of the data set drew no conclusions. This is harder to observe a relationship as one would have to account for salary inflation
in the league, and a pitcher from 2015 that was in the higher bracket may be considered a lower paid pitcher in 2019, where the highest paid relief pitcher in 2015 received $10 million vs
$20 million in 2019. 