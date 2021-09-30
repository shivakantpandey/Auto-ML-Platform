from pandas import read_csv, read_excel
from numpy import array
from pathlib import Path
from sys import exit
from matplotlib import pyplot as plt
from time import time
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.neural_network import MLPRegressor
from datetime import datetime

def Log(data):
    with open("log.txt",'a') as log:
        log.write(f"[ {datetime.now()} ] - ")
        log.write(data)
        log.write('\n')

class Data:
    def __init__(self,filename):
        self.filename=filename
        self.read_file()
        self.plot_location="static/plots/dataset_plots/"
    def get_extension(self):
        self.ext=Path(self.filename).suffix.split('.')[1]
    def read_file(self):
        self.get_extension()
        if self.ext == 'csv':
            self.dataset=read_csv(self.filename)
        else:
            self.dataset=read_excel(self.filename)
    def get_columns(self):
        result=[]
        for col in self.dataset.columns:
            result.append(col)
        return result
    def show_metadata_console(self):
        Log(f"Metadata :  {self.filename}")
        Log("Column Name",end="")
        for i in range(35-len("Column Name")):
            Log(end=" ")
        Log(" Data Type")
        Log("-------------------------------------------------------------")
        for col in self.dataset.columns:
            Log(col,end="")
            for i in range(30-len(col)):
                Log(end=" ")
            Log("|   "+str(type(self.dataset[str(col)][0])))
    def show_metadata_ui(self):
        result='<div class="metadata"><table>'
        result+="<tr><th>Column Name</th><th>Data Type</th><th>Null count</th></tr>"
        for col in self.dataset.columns:
            result+="<tr>"
            result+=f"<td>{col}</td>"
            result+=f"<td>{str(self.dataset[str(col)].dtypes)}</td>"
            result+=f"<td>{self.dataset[str(col)].isnull().sum()}</td>"
            result+="</tr>"
        result+="</table></div>"
        return result
    def show_statistics(self):
        result='<div class="statistics"><table>'
        result+="<tr><th>Column Name</th><th>Count</th><th>Minimum</th><th>Maximum</th><th>Standard Deviation</th><th>Mean</th></tr>"
        for col in self.dataset.columns:
            if type(self.dataset[str(col)][0]) == type(""):
                col_stats=[self.dataset[str(col)].count()]
                mode=0
            else:
                col_stats=[self.dataset[str(col)].count(),
                self.dataset[str(col)].min(),
                self.dataset[str(col)].max(),
                self.dataset[str(col)].std(),
                self.dataset[str(col)].mean()
                ]
                mode=1
            result+="<tr>"
            result+=f"<td>{col}</td>"
            result+=f"<td>{col_stats[0]}</td>"
            if mode==0:
                result+="<td>Not Applicable</td>"
                result+="<td>Not Applicable</td>"
                result+="<td>Not Applicable</td>"
                result+="<td>Not Applicable</td>"
            else:
                result+=f"<td>{col_stats[1]}</td>"
                result+=f"<td>{col_stats[2]}</td>"
                result+=f"<td>{col_stats[3]}</td>"
                result+=f"<td>{col_stats[4]}</td>"
            result+="</tr>"
        result+="</table></div>"
        return result
    def denoise(self,mode):
        if mode==0:
            # fill the NANs with the mean
            values=self.dataset.mean(skipna=True).to_dict()    
            self.dataset=self.dataset.fillna(value=values)
        elif mode==1:
            # fill the NANs with the median
            values=self.dataset.median(skipna=True).to_dict()
            self.dataset=self.dataset.fillna(value=values)
        elif mode==2:
            # drop NANs rows.
            self.dataset=self.dataset.dropna()
            self.dataset=self.dataset.reset_index(drop=True)

    def vectorize(self,predictor_cols,target_cols):
        X=[]
        Y=[]
        temp=[]
        predictor_cols=array(predictor_cols)
        target_cols=array(target_cols)
        for col in predictor_cols:
            temp.append(self.dataset[str(col)].values)
        temp=array(temp)
        for i in range(temp.shape[1]):
            dims=[]
            for j in range(temp.shape[0]):
                dims.append(temp[j][i])
            X.append(dims)
        temp=[]
        for col in target_cols:
            temp.append(self.dataset[str(col)].values)
        temp=array(temp)
        for i in range(temp.shape[1]):
            dims=[]
            for j in range(temp.shape[0]):
                dims.append(temp[j][i])
            Y.append(dims)
        return X,Y
    def plot(self,mode=0,name='default_plot',val_range=(0,100),area=5,color='green',alpha=0.5):
        fnames=[]
        for col1 in self.dataset.columns:
            for col2 in self.dataset.columns:
                if(col1!=col2 and (type(self.dataset[str(col1)][0]) != type("")) and (type(self.dataset[str(col2)][0]) != type("")) ):
                    if mode==0:
                        # scatter plot
                        plt.clf()
                        plt.xlabel(f"{col1}")
                        plt.ylabel(f"{col2}")
                        plt.title(f"{col1} versus {col2} Scatter Plot")
                        plt.scatter(self.dataset[str(col1)].values[val_range[0]:val_range[1]],self.dataset[str(col2)].values[val_range[0]:val_range[1]],s=area,c=color,alpha=alpha)
                        plt.savefig(f"{self.plot_location}{name}_{col1}_{col2}.png")
                        plt.clf()
                        fnames.append(f"{self.plot_location}{name}_{col1}_{col2}.png")
                    elif mode==1:
                        # line plot
                        plt.clf()
                        plt.xlabel(f"{col1}")
                        plt.ylabel(f"{col2}")
                        plt.title(f"{col1} versus {col2} Line Plot")
                        plt.plot(self.dataset[str(col1)].values[val_range[0]:val_range[1]],self.dataset[str(col2)].values[val_range[0]:val_range[1]],s=area,c=color,alpha=alpha)
                        plt.savefig(f"{self.plot_location}{name}_{col1}_{col2}.png")
                        plt.clf()
                        fnames.append(f"{self.plot_location}{name}_{col1}_{col2}.png")
                    else:
                        print("Problem")
        return fnames                        

class Analytics:
    def __init__(self,fname,denoise_mode=0):
        self.scaler=StandardScaler()
        self.plot_location='static/plots/model_plots/'
        start=time()
        self.data=Data(fname)
        Log(f"Read the dataset in {time() - start} seconds.")
        start=time()
        self.data.denoise(denoise_mode)
        Log(f"Denoised the dataset in {time() - start} seconds.")
    def get_plot(self,name,mode,val_range=(0,100)):
        start=time()
        plots=self.data.plot(mode=mode,name=name,val_range=val_range)
        Log(f"Plotted the entire dataset in {time() - start} seconds.")
        return plots
    def get_metadata_info(self,mode=1):
        if mode==0:
            self.data.show_metadata_console()
        else:
            start=time()
            info=self.data.show_metadata_ui()
            Log(f"Metadata retreived for dataset in {time() - start} seconds.")
            return info
    def get_stats_info(self):
        start=time()
        info=self.data.show_statistics()
        Log(f"Statistical information retreived for dataset in {time() - start} seconds.")
        return info
    def preprocess(self,predictor_cols,target_cols):
        start=time()
        X,Y=self.data.vectorize(predictor_cols,target_cols)
        X=self.scaler.fit_transform(X)
        self.X=array(X)
        self.Y=array(Y)
        Log(f"Preprocessing applied to predictor variable set in {time() - start} seconds.")
    def model(self,name,model_name="LR",split_ratio=0.2):
        """
                ##### Abbreviations for model name #####
        LR : Linear Regression
        RF : Random Forest
        GBR : Gradient Boosting Regressor
        MLP : Multi Layered Perceptron
        """
        result={}
        model_alg=""
        start=time()
        X_train, X_test, Y_train, Y_test=train_test_split(self.X,self.Y,test_size=split_ratio)
        Log(f"Data split peformed in {time() - start} seconds.")
        start=time()
        if model_name=='LR':
            pred_model=LinearRegression()
            model_alg="Linear Regression"
        elif model_name=='RF':
            pred_model=RandomForestRegressor()
            model_alg="Random Forest Regression"
        elif model_name=='GBR':
            pred_model=GradientBoostingRegressor()
            model_alg="Gradient Boosting Regression"
        elif model_name=='MLP':
            pred_model=MLPRegressor(hidden_layer_sizes=(2 * X_train.shape[0],4 * X_train.shape[0],2 * X_train.shape[0]))
            model_alg="Multi Layered Perceptron Regression"
        Log(f"Model initialized in {time() - start} seconds.")
        start=time()
        pred_model.fit(X_train,Y_train)
        Log(f"Training completed in {time() - start} seconds.")
        start=time()
        r2_score=pred_model.score(X_test,Y_test)
        Log(f"Validation score calculated in {time() - start} seconds.")
        start=time()
        prediction=pred_model.predict(X_test)
        Log(f"Prediction for test set completed in {time() - start} seconds.")
        start=time()
        dummy=array([i for i in range(len(prediction))])
        plt.title(f"Predicted [{model_alg}] versus Actual")
        plt.plot(Y_test,dummy,'gray',prediction,dummy,'green')
        plt.savefig(f"{self.plot_location}{name}.png")
        Log(f"Test set prediction visuals created in {time() - start} seconds.")
        result["R2_score"]=r2_score
        result["Model_Plot"]=f"{self.plot_location}{name}.png"
        result["Model"]=model_alg
        return result
    def get_data_columns(self):
        result=self.data.get_columns()
        return result




            
            










