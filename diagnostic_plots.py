
# coding: utf-8

# In[4]:

get_ipython().magic(u'matplotlib inline')

def diagnostic_print(y_test,y_pred,y_proba,model_name):
    
    from sklearn.ensemble import RandomForestClassifier
    from xgboost import XGBClassifier
    from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
    from sklearn.metrics import roc_curve, auc
    import matplotlib.pyplot as plt
    
    print('=====Performance of '+model_name+'=====')
    print('Accuracy: {:.4f}'.format(accuracy_score(y_test, y_pred)))
    print('Precision: {:.4f}'.format(precision_score(y_test, y_pred)))
    print('Recall: {:.4f}'.format(recall_score(y_test, y_pred)))
    print('F1: {:.4f}'.format(f1_score(y_test, y_pred)))
    print(confusion_matrix(y_test, y_pred))

    # Compute ROC curve and ROC area for each class
    fpr = dict()
    tpr = dict()
    roc_auc = dict()
    fpr, tpr, _ = roc_curve(y_test, y_proba)
    roc_auc = auc(fpr, tpr)
    print('ROC AUC =', roc_auc)

    # Plot ROC-AUC
    plt.figure()
    plt.plot(fpr, tpr, color='darkorange',
             lw=2, label='ROC curve (area = %0.4f)' % roc_auc)
    plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title('ROC curve')
    plt.legend(loc="lower right")
    plt.show()

    
if __name__ == "__main__":
    import pandas as pd
    y_train = pd.read_pickle('y_train')
    y_test = pd.read_pickle('y_test')
    diagnostic_print(y_test,y_test,y_test,'testing')


# In[ ]:



