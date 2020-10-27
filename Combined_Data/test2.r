library(caret)
library(doSNOW)
library(infotheo)
library(FSelector)
library(pROC)
library(plyr)
library(dplyr)
library(DMwR)

cl<-makeCluster(4) #number of CPU cores
registerDoSNOW(cl)

filter_features_MTCOOC <- function(data){
  # MODIFIE ICI
  aoinames = c('Text Content Area','Subgoals','Agent','Image Content Area','Table of Contents','Timer','Overall Learning Goal','SRL Palette')

  toremove = c("length", "numfixations", "numsaccades", "numsegments", "numsamples",	"sumabspathangles" ,"sumrelpathangles", "sumfixationduration", "sumpathdistance", "sumsaccadedistance", "sumsaccadeduration")

  #"endpupilsize", "startpupilsize", "meanpupilsize", "minpupilsize", "maxpupilsize", "stddevpupilsize", "meanpupilvelocity", "stddevpupilvelocity", "minpupilvelocity", #"maxpupilvelocity")

  for(i in 1:length(aoinames)){
    for(j in 1:length(aoinames)){
      toremove = c(toremove, paste(aoinames[i], "numtransfrom", aoinames[j], sep="_"))
    }
  }

  data = data[, !(colnames(data) %in% c(toremove))]
  #data=select_if(data, is.numeric)
  return(data)
}

sample0 <- function(x, ...) x[sample.int(length(x), ...)]

CVsamples <- function(ids, K=10, forcedK = FALSE)
{
  if (!exists(".Random.seed", envir=.GlobalEnv, inherits = FALSE)) runif(1)
  seed <- get(".Random.seed", envir=.GlobalEnv, inherits = FALSE)
  n <- length(ids)
  #n <- nrow(ids)
  if ((K > n) || (K <= 1))
    stop("'K' outside allowable range")
  K.o <- K
  K <- round(K)

  if(forcedK == FALSE){
    kvals <- unique(round(n/(1L:floor(n/2))))
    temp <- abs(kvals-K)
    if (!any(temp == 0))
      K <- kvals[temp == min(temp)][1L]
    if (K!=K.o) warning(gettextf("'K' has been set to %f", K), domain = NA)
  }
  f <- ceiling(n/K)
  s <- sample0(rep(1L:K, f), n)

  list (seed=seed, samples=s, K=K)
}

CVsamplesStratified <- function(classdata, K=10, iter=1)
{
  if (!exists(".Random.seed", envir=.GlobalEnv, inherits = FALSE)) runif(1)
  seed <- get(".Random.seed", envir=.GlobalEnv, inherits = FALSE)

  n <- nrow(classdata)
  if ((K > n) || (K <= 1))
    stop("'K' outside allowable range - stratified")
  K.o <- K
  K <- round(K)
  kvals <- unique(round(n/(1L:floor(n/2))))
  temp <- abs(kvals-K)
  if (!any(temp == 0))
    K <- kvals[temp == min(temp)][1L]
  if (K!=K.o) warning(gettextf("'K' has been set to %f", K), domain = NA)

  baseClass1 = sum(classdata$LengthC1) / ( sum(classdata$LengthC1) + sum(classdata$LengthC2) )
  nbClass1dataset = round(sum(classdata$LengthC1) / K)

  partFrequent = subset(classdata, PropClass1 > baseClass1)
  partInfrequent = subset(classdata, PropClass1 <= baseClass1)

  foldC1 = CVsamples(partFrequent$Part_id, K, TRUE)
  foldC2 = CVsamples(partInfrequent$Part_id, K, TRUE)

  partFrequent = cbind(partFrequent, Fold = foldC1$samples)
  partInfrequent = cbind(partInfrequent, Fold = foldC2$samples)
  allfolds = rbind(partFrequent, partInfrequent)
  allfolds = allfolds[order(allfolds$Part_id),]
  foldstats = ddply(allfolds, .(Fold), summarize, distrib = sum(LengthC1)/(sum(LengthC1) + sum(LengthC2)), nbClass1 = sum(LengthC1))

  for(iterloop in 1:iter){
    for(i in 1:nrow(allfolds)){
      for(j in 1:nrow(allfolds)){
        if(i == j || allfolds[i,"Fold"] == allfolds[j,"Fold"])
          next

        if( (foldstats$distrib[foldstats$Fold == allfolds[i,"Fold"]] > foldstats$distrib[foldstats$Fold == allfolds[j,"Fold"]] && allfolds[i, "PropClass1"] > allfolds[j, "PropClass1"])
            || (foldstats$distrib[foldstats$Fold == allfolds[i,"Fold"]] < foldstats$distrib[foldstats$Fold == allfolds[j,"Fold"]] && allfolds[i, "PropClass1"] < allfolds[j, "PropClass1"]) ) {
          tempf = allfolds[i, "Fold"]
          allfolds[i, "Fold"] = allfolds[j, "Fold"]
          allfolds[j, "Fold"] = tempf

          foldstats = ddply(allfolds, .(Fold), summarize, distrib = sum(LengthC1)/(sum(LengthC1) + sum(LengthC2)))
        }
      }
    }
  }

  list (samples=allfolds$Fold, K=K)
}

na.zero <- function (x) {
  x[is.na(x)] <- 0
  return(x)
}

#==========================================
# MODIFIE ICI
dir = "/home/rohit/Documents/Academics/UBC/RA-Project/Data/Rohit-MT-UBC/Combined_Data/"

set.seed(78)
feat_selection = TRUE
K = 8
runs = 10
dependant = "Class"
dep_label = c("frustration_boredom")
datasets = c("data_full_prev_3.csv")
window_labels = c("full_prev_3")

#out result file
# MODIFIE ICI
dir = "/home/rohit/Documents/Academics/UBC/RA-Project/Data/Rohit-MT-UBC/Combined_Data/"

set.seed(78)
feat_selection = TRUE
K = 8
runs = 10
dependant = "Class"
dep_label = c("frustration_boredom")
datasets = c("data_full_prev_3.csv")
window_labels = c("full_prev_3")

#out result file
# MODIFIE ICI
dirout = "/home/rohit/Documents/Academics/UBC/RA-Project/Data/Rohit-MT-UBC/Combined_Data/"
out = paste(dirout, "predic_MT_COOC_4classes.csv", sep="")
#out = paste(dirout, "predic_MT_valencepredbinarylumpednegative.csv", sep="")
#out = paste(dirout, "predic_MT_anxious.csv", sep="")
sink(out)
print("Dataset,EIVthreholds,Window,Classifier,Accuracy,Kappa,Base,Sensi,Speci,F1")
sink()

outwithinfolds = paste(dirout, "predic_MT_COOC_4classes_withinfolds.csv", sep="")
#outwithinfolds = paste(dirout, "predic_MT_valencepredbinarylumpednegative_withinfolds.csv", sep="")
#outwithinfolds = paste(dirout, "predic_MT_anxious_withinfolds.csv", sep="")
sink(outwithinfolds)
print("Dataset,Window,Runs,K,Classifier,Accuracy")
sink()

outconfmatrix = paste(dirout, "predic_MT_COOC_4classes_confusionmatrix.txt", sep="")
#outwithinfolds = paste(dirout, "predic_MT_valencepredbinarylumpednegative_withinfolds.csv", sep="")
#outwithinfolds = paste(dirout, "predic_MT_anxious_withinfolds.csv", sep="")
sink(outconfmatrix)
sink()

#==========================================
current_run = 1

#prediction for all time slices
for(dataset_i in datasets){
  print(paste("Dataset", dataset_i))

  #========================================== open and preprocess data
  filename = paste(dir, dataset_i, sep="")
  data = read.csv(filename)
  #data = preprocess_features(data)

  #data = droplevels(data)

  #========================================== build and train classifiers
  accLB = 0 #acc
	kappaLB = 0 #kappa
	sensiLB = c(0, 0, 0, 0)
	speciLB = c(0, 0, 0, 0)
	F1LB = c(0, 0, 0, 0)
	conftableLB = NULL

	accRF = 0 #acc
	kappaRF = 0 #kappa
	sensiRF = c(0, 0, 0, 0)
	speciRF = c(0, 0, 0, 0)
	F1RF = c(0, 0, 0, 0)
	conftableRF = NULL

	accNN = 0 #acc
	kappaNN = 0 #kappa
	sensiNN = c(0, 0, 0, 0)
	speciNN = c(0, 0, 0, 0)
	F1NN = c(0, 0, 0, 0)
	conftableNN = NULL

	accSVM = 0 #acc
	kappaSVM = 0 #kappa
	sensiSVM = c(0, 0, 0, 0)
	speciSVM = c(0, 0, 0, 0)
	F1SVM = c(0, 0, 0, 0)
	conftableSVM = NULL

	accNB = 0 #acc
	kappaNB = 0 #kappa
	sensiNB = c(0, 0, 0, 0)
	speciNB = c(0, 0, 0, 0)
	F1NB = c(0, 0, 0, 0)
	conftableNB = NULL

  #Start building classifiers
  for (run_i in 1:runs) #multiple runs of CV
  {
    print(paste("Runs", run_i))

    #K folds CV
    tempdata = aggregate(data$Class ~ data$Part_id, FUN=summary)
    tempdata$PropClass1 = tempdata[,2][,1] / (tempdata[,2][,1] + tempdata[,2][,2])
    tempdata = data.frame(Part_id = tempdata[,1], LengthC1 = tempdata[,2][,1], LengthC2 = tempdata[,2][,2], PropClass1 = tempdata$PropClass1)
    #folds <- CVsamples(unique(data$Part_id), K)
    folds <- CVsamplesStratified(tempdata, K)

    #seed <- folds$seed
    s <- folds$samples
    ms <- max(s)
    realK = folds$K

    for(i in seq_len(ms)) {	#K-folds cross-validation

      tempaccLB = 0
      tempaccRF = 0
      tempaccNN = 0
      tempaccSVM = 0
      tempaccNB = 0

      j.out <- unique(data$Part_id)[(s == i)]
      j.in <- unique(data$Part_id)[(s != i)]
      index.out <- which(data$Part_id %in% j.out)
      index.in <- which(data$Part_id %in% j.in)
      traindata <- data[index.in, , drop=FALSE]
      testdata <- data[index.out, , drop=FALSE]

      #========================================== features selection
      #feat selection
			traindata = filter_features_MTCOOC(traindata) #select features
			testdata = filter_features_MTCOOC(testdata) #select features
			#summary(traindata)
			#summary(testdata)

			if(feat_selection){
				#fmla <- as.formula(paste("traindata$", dependant,"~", paste("traindata$", colnames(traindata[, colnames(traindata) != dependant]), collapse= "+", sep=""), sep=""))
				#subset = cfs(fmla, traindata)
				#fmla <- as.simple.formula(  paste(subset),   paste("traindata$", dependant, sep=""))

				removeZeros = apply(traindata, 2, function(x) length(unique(x)) == 1) # remove zeros
				traindata = traindata[, !removeZeros]

				#data_cor = cor(traindata[, colnames(traindata) != dependant])
				data_cor[is.na(data_cor)] = 1
				corfeat = findCorrelation(data_cor, cutoff = .9)
				traindata =  traindata[,-corfeat]
				#fmla <- as.formula(paste("traindata$", dependant,"~", paste("traindata$", colnames(traindata[, colnames(traindata) != dependant]), collapse= "+", sep=""), sep=""))
				fmla <- as.formula(paste(dependant,"~", paste(colnames(traindata[, colnames(traindata) != dependant]), collapse= "+", sep=""), sep=""))
			}else{
				removeZeros = apply(traindata, 2, function(x) length(unique(x)) == 1) # remove zeros
				traindata = traindata[, !removeZeros]
				fmla <- as.formula(paste("traindata$", dependant,"~", paste("traindata$", colnames(traindata[, colnames(traindata) != dependant]), collapse= "+", sep=""), sep=""))
			}
			#========================================== sampling and features selection

			ctrl <- trainControl(method = "none", allowParallel=T)
			#ctrl <- trainControl(method = "repeatedcv", number = 8, repeats=5, allowParallel=T)

			#baseline
			#base = max(summary(data[, dependant])[1], summary(data[, dependant])[2], summary(data[, dependant])[3]) / nrow(data)
			base = max(summary(data[, dependant])[1], summary(data[, dependant])[2], summary(data[, dependant])[3], summary(data[, dependant])[4]) / nrow(data)
			withinfoldbase = max(summary(testdata[, dependant])[1], summary(testdata[, dependant])[2], summary(testdata[, dependant])[3], summary(testdata[, dependant])[4]) / nrow(testdata)

			#LogicBoost
			tuneparam	 <-  expand.grid( nIter=c(50))
			fitLB <- train(fmla,
							 data = traindata,
							 method = "LogitBoost",
							 trControl = ctrl,
							 tuneGrid = tuneparam,
							 metric="Accuracy")

			res = predict(fitLB, newdata=testdata)
			resCM = confusionMatrix(res, testdata[,dependant])
			resCM$byClass = na.zero(resCM$byClass)

			accLB = accLB + resCM$overall[1] #acc
			tempaccLB = tempaccLB + resCM$overall[1] #acc
			kappaLB = kappaLB + resCM$overall[2] #kappa
			sensiLB = sensiLB + c(resCM$byClass[1,1], resCM$byClass[2,1], resCM$byClass[3,1], resCM$byClass[4,1])
			speciLB = speciLB + c(resCM$byClass[1,2], resCM$byClass[2,2], resCM$byClass[3,2], resCM$byClass[4,2])
			F1LB = F1LB + c(resCM$byClass[1,7], resCM$byClass[2,7], resCM$byClass[3,7], resCM$byClass[4,7])
			# sensiLB = sensiLB + c(resCM$byClass[1])
			# speciLB = speciLB + c(resCM$byClass[2])
			# F1LB = F1LB + c(resCM$byClass[7])
			if (is.null(conftableLB)){
				conftableLB = resCM$table
			}else{
				conftableLB = conftableLB + resCM$table
			}

			#Random Forest
			tuneparam	 <-  expand.grid(mtry=c(sqrt(ncol(traindata))))
			fitRF <- train(fmla,
								 data = traindata,
								 method = "rf",
								 trControl = ctrl,
								 tuneGrid = tuneparam,
								 metric="Accuracy")

			res = predict(fitRF, newdata=testdata)
			resCM = confusionMatrix(res, testdata[,dependant])
			resCM$byClass = na.zero(resCM$byClass)

			accRF = accRF + resCM$overall[1] #acc
			tempaccRF = tempaccRF+resCM$overall[1] #acc
			kappaRF = kappaRF + resCM$overall[2] #kappa
			sensiRF = sensiRF + c(resCM$byClass[1,1], resCM$byClass[2,1], resCM$byClass[3,1], resCM$byClass[4,1])
			speciRF = speciRF + c(resCM$byClass[1,2], resCM$byClass[2,2], resCM$byClass[3,2], resCM$byClass[4,2])
			F1RF = F1RF + c(resCM$byClass[1,7], resCM$byClass[2,7], resCM$byClass[3,7], resCM$byClass[4,7])
			# sensiRF = sensiRF + c(resCM$byClass[1])
			# speciRF = speciRF + c(resCM$byClass[2])
			# F1RF = F1RF + c(resCM$byClass[7])
			if (is.null(conftableRF)){
				conftableRF = resCM$table
			}else{
				conftableRF = conftableRF + resCM$table
			}

			#NN
			tuneparam	 <-  expand.grid(decay=c(0.05), size=c(4), bag=c(FALSE))
			fitNN <- train(fmla,
								 data = traindata,
								 method = "avNNet", #avNNet bag' was held constant at a value of FALSE
								 trControl = ctrl,
								 tuneGrid = tuneparam,
								 metric="Accuracy",
								 MaxNWts=5000)

			res = predict(fitNN, newdata=testdata)
			resCM = confusionMatrix(res, testdata[,dependant])
			resCM$byClass = na.zero(resCM$byClass)

			accNN = accNN + resCM$overall[1] #acc
			tempaccNN = tempaccNN+resCM$overall[1] #acc
			kappaNN = kappaNN + resCM$overall[2] #kappa
			sensiNN = sensiNN + c(resCM$byClass[1,1], resCM$byClass[2,1], resCM$byClass[3,1], resCM$byClass[4,1])
			speciNN = speciNN + c(resCM$byClass[1,2], resCM$byClass[2,2], resCM$byClass[3,2], resCM$byClass[4,2])
			F1NN = F1NN + c(resCM$byClass[1,7], resCM$byClass[2,7], resCM$byClass[3,7], resCM$byClass[4,7])
			# sensiNN = sensiNN + c(resCM$byClass[1])
			# speciNN = speciNN + c(resCM$byClass[2])
			# F1NN = F1NN + c(resCM$byClass[7])
			if (is.null(conftableNN)){
				conftableNN = resCM$table
			}else{
				conftableNN = conftableNN + resCM$table
			}

			#SVM
			tuneparam	 <-  expand.grid(sigma=c(0.05), C=c(1))
			fitSVM <- train(fmla,
								 data = traindata,
								 method = "svmRadial",
								 trControl = ctrl,
								 tuneGrid = tuneparam,
								 metric="Accuracy")

			res = predict(fitSVM, newdata=testdata)
			resCM = confusionMatrix(res, testdata[,dependant])
			resCM$byClass = na.zero(resCM$byClass)

			accSVM = accSVM + resCM$overall[1] #acc
			tempaccSVM = tempaccSVM+resCM$overall[1] #acc
			kappaSVM = kappaSVM + resCM$overall[2] #kappa
			sensiSVM = sensiSVM + c(resCM$byClass[1,1], resCM$byClass[2,1], resCM$byClass[3,1], resCM$byClass[4,1])
			speciSVM = speciSVM + c(resCM$byClass[1,2], resCM$byClass[2,2], resCM$byClass[3,2], resCM$byClass[4,2])
			F1SVM = F1SVM + c(resCM$byClass[1,7], resCM$byClass[2,7], resCM$byClass[3,7], resCM$byClass[4,7])
			# sensiSVM = sensiSVM + c(resCM$byClass[1])
			# speciSVM = speciSVM + c(resCM$byClass[2])
			# F1SVM = F1SVM + c(resCM$byClass[7])
			if (is.null(conftableSVM)){
				conftableSVM = resCM$table
			}else{
				conftableSVM = conftableSVM + resCM$table
			}

			#NB
			# tuneparam	 <-  expand.grid(fL=c(0), usekernel=False, adjust=False)
			# fitNB <- train(fmla,
								 # data = traindata,
								 # method = "nb",
								 # trControl = ctrl,
								 # tuneGrid = tuneparam,
								 # metric="Accuracy")

			# res = predict(fitNB, newdata=testdata)
			# resCM = confusionMatrix(res, testdata[,dependant])
			# resCM$byClass = na.zero(resCM$byClass)

			# accNB = accNB + resCM$overall[1] #acc
			# tempaccNB = tempaccNB+resCM$overall[1] #acc
			# kappaNB = kappaNB + resCM$overall[2] #kappa
			# #sensiNB = sensiNB + c(resCM$byClass[1,1], resCM$byClass[2,1], resCM$byClass[3,1], resCM$byClass[4,1])
			# #speciNB = speciNB + c(resCM$byClass[1,2], resCM$byClass[2,2], resCM$byClass[3,2], resCM$byClass[4,2])
			# #F1NB = F1NB + c(resCM$byClass[1,7], resCM$byClass[2,7], resCM$byClass[3,7], resCM$byClass[4,7])
			# sensiNB = sensiNB + c(resCM$byClass[1])
			# speciNB = speciNB + c(resCM$byClass[2])
			# F1NB = F1NB + c(resCM$byClass[7])
			# if (is.null(conftableNB))
				# conftableNB = resCM$table
			# else
				# conftableNB = conftableNB + resCM$table


		sink(outwithinfolds, append = TRUE)
		#EIVthr = substr(dataset_i, nchar(dataset_i)-4, nchar(dataset_i)-4)
		wind = window_labels[current_run]
		dep = dep_label[current_run]
		print(paste(dep, wind, run_i, realK, "Logit", tempaccLB, paste(sensiLB, collapse=','), sep=",") )
		print(paste(dep, wind, run_i, realK, "RF", tempaccRF, paste(sensiRF, collapse=','), sep=",") )
		print(paste(dep, wind, run_i, realK, "NN", tempaccNN, paste(sensiNN, collapse=','), sep=",") )
		print(paste(dep, wind, run_i, realK,"SVM", tempaccSVM, paste(sensiSVM, collapse=','), sep=",") )
		print(paste(dep, wind, run_i, realK, "OverallBase", base, sep=",") )
		print(paste(dep, wind, run_i, realK, "WithinBase", withinfoldbase, sep=",") )
		sink()


		}#end CV

		#========================================== compute means and write output

	} #end runs

	# Average over number of folds and runs
	accLB = accLB / realK / runs
	kappaLB = kappaLB / realK / runs
	sensiLB = sensiLB / realK / runs
	speciLB = speciLB / realK / runs
	F1LB = F1LB / realK / runs
	conftableLB = conftableLB / runs

	accRF = accRF / realK / runs
	kappaRF = kappaRF / realK / runs
	sensiRF = sensiRF / realK / runs
	speciRF = speciRF / realK / runs
	F1RF = F1RF / realK / runs
	conftableRF = conftableRF / runs

	accNN = accNN / realK / runs
	kappaNN = kappaNN / realK / runs
	sensiNN = sensiNN / realK / runs
	speciNN = speciNN / realK / runs
	F1NN = F1NN / realK / runs
	conftableNN = conftableNN / runs

	accSVM = accSVM / realK / runs
	kappaSVM = kappaSVM / realK / runs
	sensiSVM = sensiSVM / realK / runs
	speciSVM = speciSVM / realK / runs
	F1SVM = F1SVM / realK / runs
	conftableSVM = conftableSVM / runs

	# accNB = accNB / realK / runs
	# kappaNB = kappaNB / realK / runs
	# sensiNB = sensiNB / realK / runs
	# speciNB = speciNB / realK / runs
	# F1NB = F1NB / realK / runs
	# conftableNB = conftableNB / realK / runs

	#output results
	sink(out, append = TRUE)
	#EIVthr = substr(dataset_i, nchar(dataset_i)-4, nchar(dataset_i)-4)
	wind = window_labels[current_run]
	dep = dep_label[current_run]
	current_run = current_run + 1
	print(paste(dep, 4, wind, "Logit", accLB, kappaLB, paste(sensiLB, collapse=','), paste(speciLB, collapse=','), paste(F1LB, collapse=','), sep=",") )
	print(paste(dep, 4, wind, "RF", accRF, kappaRF, paste(sensiRF, collapse=','), paste(speciRF, collapse=','), paste(F1RF, collapse=','), sep=",") )
	print(paste(dep, 4, wind, "NN", accNN, kappaNN, paste(sensiNN, collapse=','), paste(speciNN, collapse=','), paste(F1NN, collapse=','), sep=",") )
	print(paste(dep, 4, wind, "SVM", accSVM, kappaSVM, paste(sensiSVM, collapse=','), paste(speciSVM, collapse=','), paste(F1SVM, collapse=','), sep=",") )
	#print(paste(dep, 4, wind, "NaiveBayes", accNB, kappaNB, paste(sensiNB, collapse=','), paste(speciNB, collapse=','), paste(F1NB, collapse=','), sep=",") )
	print(paste(dep, 4, wind, "Base", base, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, sep=",") )
	sink()


	sink(outconfmatrix, append = TRUE)
	print(dataset_i)
	print("LB")
	print(conftableLB)
	print("RF")
	print(conftableRF)
	print("NN")
	print(conftableNN)
	print("SVM")
	print(conftableSVM)
	print("")
	sink()

}#end dataset
