library(lme4)
library(reshape2)
library(ggplot2)
library(dplyr)
library(sampling)
library(ROCR)

lr_mixed_model<-function(model_data  # 直接可以用来建模的R dataframe对象
                         , subject_id # ID对象的名称，为字符串
                         , response  # i.e. y (1/0) 变量的名称, 为字符串
                         , predictors_vec # i.e. 包含所有预测变量名称的R vector，即字符串向量
                         , random_intercept = TRUE # 模型截距是否为随机的，取值TRUE/FALSE
){


  #形成模型的公式

  model_formula_str <- paste0(response,'~', paste(predictors_vec,collapse="+"))
  print(model_formula_str)
  #运行模型

  if(random_intercept){

    eval(parse(text = paste0("model_data <- arrange(model_data, ", subject_id, ")")))
    print(head(model_data))

    print(paste(model_formula_str, paste0('(1|', subject_id, ')'), sep = "+" ))
    model_formula <- formula(paste(model_formula_str, paste0('(1|', subject_id, ')'), sep = "+" ))
    eval(parse(text= paste0("subject_id_list <- unique(model_data$", subject_id, ")")))

    #model_outcome <- glmer(model_formula, data = model_data, family = binomial)
    model_outcome <- glmer(model_formula, data = model_data, family = binomial, control = glmerControl(optimizer = "bobyqa"),
                           nAGQ = 10)

    cat('The outcome of model with random intercept is \n')
    print(summary(model_outcome))
    cat('\n')

    fixed_effects <- fixef(model_outcome)

    random_effects <- ranef(model_outcome)

    #append id
    random_effects <- data.frame(original_id = subject_id_list, random_intercept = random_effects[[subject_id]])
    colnames(random_effects) <- c(subject_id,"intercept_random_part")

    # do prediction on model data
    predicted_probs_with_rand <- predict(model_outcome, type = 'response')

    predicted_probs_with_no_rand <- predict(model_outcome, type = 'response', re.form = NA)

    #append id
    prediction = data.frame(original_id = model_data[subject_id], predicted_probs_with_rand= predicted_probs_with_rand
                            , predicted_probs_without_rand=predicted_probs_with_no_rand)
    colnames(prediction)[1] <- subject_id

    outcome_list <- list('model_type' = 'generalized_lr'
                         , 'fixed_effects' = fixed_effects          # 固定效应
                         , 'random_effects' = random_effects              # 随机效应
                         , 'predicted_probabilities' = prediction                 # 预测概率
                         , 'fitted_model' = model_outcome)


  } else {

    model_formula <- formula(model_formula_str)

    model_outcome <- glm(model_formula, data = model_data, family = binomial)

    cat('The outcome of ordinary logistic regression is \n')
    print(summary(model_outcome))
    cat('\n')

    fixed_effects <- coef(model_outcome)
    random_effects <- NULL

    # do prediction on model data
    predicted_probs_with_no_rand <- predict(model_outcome, model_data, type = "response")

    #append id
    prediction = data.frame(original_id = model_data[subject_id], predicted_probs_with_rand= NA
                            , predicted_probs_without_rand=predicted_probs_with_no_rand)
    colnames(prediction)[1] <- subject_id

    outcome_list <- list('model_type' = 'ordinary_lr'
                         , 'fixed_effects' = fixed_effects
                         , 'random_effects' = random_effects
                         , 'predicted_probabilities' = prediction
                         , 'fitted_model' = model_outcome)

  }


  return(outcome_list)

}


