library("MASS")
library("lme4")
library("car")
library("lsr")

#read data
prediction_output = fread("C:\\Users\\Sébastien\\Documents\\Travail\\Students\\Grigorii\\results_features_preproc Aug 14~\\predict-taskchar_result_cumulative_all.csv")
#prediction_output = fread("C:\\Users\\Sébastien\\Documents\\Travail\\Students\\Grigorii\\results_features_preproc Aug 14~\\predict-taskchar_result_accrosstask.csv")

#transform factors
prediction_output$WindowType = factor(prediction_output$WindowType)
prediction_output$WindowSize = factor(prediction_output$WindowSize)
prediction_output$Window = factor(prediction_output$Window)
prediction_output$Model = factor(prediction_output$Model)

summary(prediction_output)


####################################################################################################################
# Display mean accuracy
print("Mean and SD of prediction output")

hist(prediction_output$Accuracy_mean)

aggregate(prediction_output[, "Accuracy_mean"], list(prediction_output$Model), mean)
aggregate(prediction_output[, "Accuracy_mean"], list(prediction_output$Model), sd)

aggregate(prediction_output[, "Accuracy_class1"], list(prediction_output$Model), mean)
aggregate(prediction_output[, "Accuracy_class1"], list(prediction_output$Model), sd)

aggregate(prediction_output[, "Accuracy_class2"], list(prediction_output$Model), mean)
aggregate(prediction_output[, "Accuracy_class2"], list(prediction_output$Model), sd)



####################################################################################################################
#Basic anova: Look for impact of Model on Accuracy
print("ANOVA")

anova_meara = aov(prediction_output$Accuracy_mean~prediction_output$Model, data=prediction_output)
resmeara = summary(anova1_meara)
resmeara
etaSquared(anova_meara)

anova_meara1 = aov(prediction_output$Accuracy_class1~prediction_output$Model, data=prediction_output)
resmeara1 = summary(anova_meara1)
etaSquared(anova_meara1)

anova_meara2 = aov(prediction_output$Accuracy_class2~prediction_output$Model, data=prediction_output)
resmeara1 = summary(anova_meara2)
etaSquared(anova_meara2)


####################################################################################################################

#Adjust the p-values to account for multiple comparisons and print final raw and adjusted p
namesframe = c("Accuracy_mean", "Accuracy_class1", "Accuracy_class2")
Model_p = data.frame("test"=namesframe, "p"=c(resmeara[[1]]$'Pr(>F)'[[1]], resmeara1[[1]]$'Pr(>F)'[[1]], resmeara2[[1]]$'Pr(>F)'[[1]]))

print("Adjusted pairwise comparisons for Model")
Model_p = Model_p[order(Model_p$p),]
Model_p$adjust.p = p.adjust(Model_p$p, method = "fdr")
Model_p



















