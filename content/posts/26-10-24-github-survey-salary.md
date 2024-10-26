---
title: What technology skills result in the highest compensation?
description: Analysis of 2024 Stack Overflow Developer Survey data.
tldr: Learn Cloud, Kuberneties and AWS skills.
draft: false
date: "2024-10-25"
lastmod: 2024-10-25"
tags:
  - engineering
toc: true
---

## Method

I've got a particular interest in professional skill development. Soft skills are timeless and an area that should always be worked on. Whats less timeless are technology skills; with the technology landscape rapidly evolving, practitioners must continuously review and develop their skills to stay competitive.

To discover out some of the skills worth focusing on, I have undertaken an analysis of the 2024 Stack Overflow Developer Survey dataset. This dataset is built from anonymous volunteered survey results covering the respondents' education, total compensation, years of experiance, and use of programming languages and frameworks.

A partial correlation was conducted to explore the relationship between these factors and compensation. The output of the correlational analysis provided a correlation for each factor, with only factors with p-values above 0.05 being considered statistically significant.

For this analysis, the dataset has been filtered to include only full-time professional developers who provided their total compensation information. Developer compensation varies due to local economic conditions, so even if total compensation were normalised to a single currency, comparisons between respondents in different countries would not yield valid results. Instead, each correlation will be evaluated independently for each country.

After filtering, the country's with the most respondents where US, Germany and the UK; for interests sake I also included Australia even though very few data points where available. With these four countries selected. Lets look at the correlations.

| **Country**                                          | **Filtered Response Count** |
| ---------------------------------------------------- | --------------------------- |
| United States of America                             | 4667                        |
| Germany                                              | 1758                        |
| United Kingdom of Great Britain and Northern Ireland | 1333                        |
| Ukraine                                              | 1179                        |
| India                                                | 1150                        |
| Canada                                               | 853                         |
| France                                               | 790                         |
| Brazil                                               | 632                         |
| Poland                                               | 540                         |
| Netherlands                                          | 536                         |
| Spain                                                | 513                         |
| Italy                                                | 498                         |
| Sweden                                               | 474                         |
| Australia                                            | 459                         |

## Statistical Significance Of Factors

Many of the factors where not statically significant as shown below. Only the most strongly correlated factors where strong enough to be statistically significant.

![](/images/26-10-24-github-servey-salary/factors_and_p_value.png)

Its also important to note that many factors were only statistically significant in a particular region. The smaller datasets, especially Australia, had less statistically significant correlations than the US.

![](/images/26-10-24-github-servey-salary/regionalpvalue.png)

## Results

So firstly, here are some factors which where statistically significant in all countries. In the below table, look at the r values, this is the correlation with reported total compensation. 

|                                                       | **GER_r** |  **UK_r** | **USA_r** |  **AU_r** | **AVG_r** |
| ----------------------------------------------------: | --------: | --------: | --------: | --------: | --------: |
|                                           **WorkExp** |  0.514256 |  0.412203 |  0.382118 |  0.430147 |  0.434681 |
|                 **ToolsTechHaveWorkedWith_Terraform** |  0.198164 |  0.167319 |  0.183067 |  0.124752 |  0.168326 |
|                **ToolsTechHaveWorkedWith_Kubernetes** |  0.157696 |  0.219061 |  0.157023 |  0.119103 |  0.163221 |
|               **MiscTechHaveWorkedWith_Apache Kafka** |  0.125133 |  0.163341 |  0.149304 |  0.197993 |  0.158943 |
|                  **ToolsTechHaveWorkedWith_Homebrew** |  0.095859 |  0.122910 |  0.170613 |  0.184254 |  0.143409 |
|                    **ToolsTechHaveWorkedWith_Docker** |  0.073619 |  0.151586 |  0.118815 |  0.146483 |  0.122626 |
|                         **LanguageHaveWorkedWith_Go** |  0.070691 |  0.100121 |  0.125164 |  0.140733 |  0.109177 |
| **MiscTechHaveWorkedWith_.NET Framework (1.0 - 4.8)** | -0.078447 | -0.130054 | -0.170868 | -0.111637 | -0.122752 |
|                 **LanguageHaveWorkedWith_JavaScript** | -0.196424 | -0.116793 | -0.137608 | -0.138596 | -0.147355 |
|                        **LanguageHaveWorkedWith_PHP** | -0.176109 | -0.167646 | -0.149162 | -0.164482 | -0.164350 |
|                   **LanguageHaveWorkedWith_HTML/CSS** | -0.207864 | -0.178049 | -0.205629 | -0.122361 | -0.178476 |

It can be seen, as expected, that years of work experience very strongly correlate with compensation. Next we can see some of my favorite tools such as Terraform, Kuberneties, Homebrew and Docker. In my mind this confirms that DevOps and cloud skill sets are really worth investing professional development effort into.

Lets JUST look at the strong positive correlations (greater than 0.1) which existed in each region. Australian data is all over the place, and can be disregarded in my view.

### USA Strong Positive Correlations

|                                                      | **GER_r** | **UK_r** | **USA_r** | **AU_r** | **AVG_r** |
| ---------------------------------------------------: | --------: | -------: | --------: | -------: | --------: |
| **PlatformHaveWorkedWith_Amazon Web Services (AWS)** |  0.201221 | 0.186091 |  0.194690 | 0.081035 |  0.165759 |
|                                   **EdLevel_master** |  0.315944 | 0.133310 |  0.130262 | 0.045489 |  0.156251 |
|                      **LanguageHaveWorkedWith_Ruby** |  0.093294 | 0.033283 |  0.116040 | 0.065094 |  0.076928 |
|                     **ToolsTechHaveWorkedWith_Make** |  0.055577 | 0.133135 |  0.105124 | 0.035826 |  0.082415 |

### UK Strong Positive Correlations

|                                                      | **GER_r** | **UK_r** | **USA_r** |  **AU_r** | **AVG_r** |
|-----------------------------------------------------:|----------:|---------:|----------:|----------:|----------:|
| **PlatformHaveWorkedWith_Amazon Web Services (AWS)** | 0.201221  | 0.186091 | 0.194690  | 0.081035  | 0.165759  |
|                 **EdLevel_bachelor**                 | 0.283945  | 0.158804 | 0.088624  | 0.029646  | 0.140255  |
|        **PlatformHaveWorkedWith_Google Cloud**       | 0.099580  | 0.155989 | 0.090843  | 0.025879  | 0.093073  |
|                 **EdLevel_associate**                | 0.285089  | 0.148694 | 0.045865  | 0.041626  | 0.130319  |
|                  **EdLevel_master**                  | 0.315944  | 0.133310 | 0.130262  | 0.045489  | 0.156251  |
|           **ToolsTechHaveWorkedWith_Make**           | 0.055577  | 0.133135 | 0.105124  | 0.035826  | 0.082415  |
|           **LanguageHaveWorkedWith_Groovy**          | 0.079601  | 0.128558 | 0.047415  | -0.036773 | 0.054700  |
|           **EmbeddedHaveWorkedWith_Catch2**          | 0.026045  | 0.127435 | 0.019481  | -0.107573 | 0.016347  |
|         **EmbeddedHaveWorkedWith_Boost.Test**        | 0.022461  | 0.124523 | -0.024609 | -0.091282 | 0.007773  |
|          **ToolsTechHaveWorkedWith_Pulumi**          | 0.057992  | 0.105890 | 0.038728  | -0.026166 | 0.044111  |

### Germany Strong Positive Correlations

|                                                      | **GER_r** | **UK_r** | **USA_r** |  **AU_r** | **AVG_r** |
|-----------------------------------------------------:|----------:|---------:|----------:|----------:|----------:|
| **PlatformHaveWorkedWith_Amazon Web Services (AWS)** | 0.201221  | 0.186091 | 0.194690  | 0.081035  | 0.165759  |
|                 **EdLevel_bachelor**                 | 0.283945  | 0.158804 | 0.088624  | 0.029646  | 0.140255  |
|                 **EdLevel_associate**                | 0.285089  | 0.148694 | 0.045865  | 0.041626  | 0.130319  |
|                  **EdLevel_master**                  | 0.315944  | 0.133310 | 0.130262  | 0.045489  | 0.156251  |
|                **EdLevel_partialuni**                | 0.250223  | 0.097982 | 0.047313  | -0.016036 | 0.094871  |
|           **LanguageHaveWorkedWith_Scala**           | 0.109548  | 0.094396 | 0.096072  | 0.032868  | 0.083221  |
|        **ToolsTechHaveWorkedWith_Google Test**       | 0.111460  | 0.069847 | 0.018368  | 0.030101  | 0.057444  |
|        **EmbeddedHaveWorkedWith_LLVM's Clang**       | 0.114205  | 0.066005 | 0.059762  | -0.080537 | 0.039859  |
|               **EdLevel_professional**               | 0.141278  | 0.061895 | 0.061535  | -0.031677 | 0.058258  |
|                 **EdLevel_secondary**                | 0.100089  | 0.060308 | 0.011260  | 0.023674  | 0.048833  |

### Australia Strong Positive Correlations

|                                        | **GER_r** |  **UK_r** | **USA_r** | **AU_r** | **AVG_r** |
|---------------------------------------:|----------:|----------:|----------:|---------:|----------:|
|    **ToolsTechHaveWorkedWith_Yarn**    | 0.013893  | 0.064556  | 0.069670  | 0.120971 | 0.067273  |
|   **LanguageHaveWorkedWith_Solidity**  | 0.002644  | 0.051130  | 0.007171  | 0.111174 | 0.043030  |
| **LanguageHaveWorkedWith_Objective-C** | -0.042947 | -0.020378 | 0.058743  | 0.127747 | 0.030791  |

## Conclusion

So when looking at the positive strong correlations for each country, we can see that AWS skills are strongly correlate with compensation; this further confirms my belief that DevOps and Cloud skills are key. 

UK and Germany have strong correlations with education level, particularly the masters level education. Correlation is not causation, and in my experience, masters degree's are often done after many years of professional experience. We could be seeing years of experience being the causation, and the masters degree being dragged along for the ride. Or maybe a masters degree is independently strongly correlated; further analysis is needed.

This analysis use of self-reported data which introduces the possibility of inaccuracies or exaggerations. The correlations did not control for other factors, even those within the same dataset. Correlations do not necessarily infer causation. The pool of survey recipients are primarily software developers; so these results should not be projected onto other technology fields such as platform or network engineering.

[Find linked the Juypter notebook used for this analysis.](/26-10-24-github-servey-salary/25-10-24-github-survey-salary.ipynb) 