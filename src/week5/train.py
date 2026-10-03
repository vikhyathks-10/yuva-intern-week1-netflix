"""Offline-reproducible CNN training on scikit-learn's bundled UCI digits data."""
from pathlib import Path
import json, time
import numpy as np
import torch
from torch import nn
from torch.utils.data import DataLoader, TensorDataset
from sklearn.datasets import load_digits
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, f1_score, classification_report, confusion_matrix

SEED=42
LABELS=[str(i) for i in range(10)]
BASE=Path(__file__).resolve().parents[2]
OUT=BASE/'visualizations'/'week5'; MODEL=BASE/'models'/'week5'

class DigitsCNN(nn.Module):
    def __init__(self):
        super().__init__()
        self.features=nn.Sequential(nn.Conv2d(1,16,3,padding=1),nn.ReLU(),nn.MaxPool2d(2),
            nn.Conv2d(16,32,3,padding=1),nn.ReLU(),nn.MaxPool2d(2))
        self.classifier=nn.Sequential(nn.Flatten(),nn.Linear(32*2*2,64),nn.ReLU(),nn.Dropout(.20),nn.Linear(64,10))
    def forward(self,x): return self.classifier(self.features(x))

def main(epochs=30,batch_size=64):
    import matplotlib.pyplot as plt
    import seaborn as sns
    torch.manual_seed(SEED); np.random.seed(SEED)
    dataset=load_digits()
    x=dataset.images.astype('float32')/16.0; y=dataset.target.astype('int64')
    x_trainval,x_test,y_trainval,y_test=train_test_split(x,y,test_size=.15,random_state=SEED,stratify=y)
    x_train,x_val,y_train,y_val=train_test_split(x_trainval,y_trainval,test_size=(.15/.85),random_state=SEED,stratify=y_trainval)
    tx=lambda a: torch.from_numpy(a[:,None,:,:].copy())
    train=DataLoader(TensorDataset(tx(x_train),torch.tensor(y_train)),batch_size=batch_size,shuffle=True)
    valid=DataLoader(TensorDataset(tx(x_val),torch.tensor(y_val)),batch_size=batch_size)
    test=DataLoader(TensorDataset(tx(x_test),torch.tensor(y_test)),batch_size=batch_size)
    model=DigitsCNN(); loss_fn=nn.CrossEntropyLoss(); optimizer=torch.optim.Adam(model.parameters(),lr=.001)
    history={'loss':[],'val_loss':[],'accuracy':[],'val_accuracy':[]}; start=time.time(); best=float('inf'); best_state=None
    for epoch in range(epochs):
        model.train(); total=correct=seen=0
        for xb,yb in train:
            optimizer.zero_grad(); logits=model(xb); loss=loss_fn(logits,yb); loss.backward(); optimizer.step()
            total+=loss.item()*len(yb); correct+=(logits.argmax(1)==yb).sum().item(); seen+=len(yb)
        history['loss'].append(total/seen); history['accuracy'].append(correct/seen)
        model.eval(); total=correct=seen=0
        with torch.no_grad():
            for xb,yb in valid:
                logits=model(xb); total+=loss_fn(logits,yb).item()*len(yb); correct+=(logits.argmax(1)==yb).sum().item(); seen+=len(yb)
        vl=total/seen; history['val_loss'].append(vl); history['val_accuracy'].append(correct/seen)
        if vl<best: best=vl; best_state={k:v.detach().clone() for k,v in model.state_dict().items()}
        if (epoch+1)%5==0 or epoch==0: print(f"Epoch {epoch+1}/{epochs} loss={history['loss'][-1]:.4f} val_loss={vl:.4f} accuracy={history['accuracy'][-1]:.4f} val_accuracy={history['val_accuracy'][-1]:.4f}")
    model.load_state_dict(best_state); model.eval(); truth=[]; preds=[]
    with torch.no_grad():
        for xb,yb in test: preds.extend(model(xb).argmax(1).numpy()); truth.extend(yb.numpy())
    metrics={'dataset':'UCI Optical Recognition of Handwritten Digits (scikit-learn load_digits)','seed':SEED,'epochs':epochs,'batch_size':batch_size,'learning_rate':.001,'train_n':len(y_train),'validation_n':len(y_val),'test_n':len(truth),'duration_seconds':time.time()-start,
      'test_accuracy':accuracy_score(truth,preds),'test_macro_f1':f1_score(truth,preds,average='macro'),'test_weighted_f1':f1_score(truth,preds,average='weighted'),
      'labels':LABELS,'classification_report':classification_report(truth,preds,target_names=LABELS,output_dict=True),'confusion_matrix':confusion_matrix(truth,preds).tolist(),
      'history':history,'best_validation_loss':best,'incorrect_examples':[],
      'split':{'train':len(y_train),'validation':len(y_val),'test':len(y_test),'method':'stratified 70/15/15; random_state=42'},'input_shape':[1,8,8]}
    bad=np.flatnonzero(np.array(truth)!=np.array(preds))[:15]
    for i in bad: metrics['incorrect_examples'].append({'index':int(i),'actual':str(truth[i]),'predicted':str(preds[i])})
    OUT.mkdir(parents=True,exist_ok=True); MODEL.mkdir(parents=True,exist_ok=True)
    torch.save(model.state_dict(),MODEL/'digits_cnn.pt')
    with (MODEL/'metrics.json').open('w',encoding='utf8') as f: json.dump(metrics,f,indent=2)
    fig,ax=plt.subplots(1,2,figsize=(11,4)); ax[0].plot(history['loss'],label='train');ax[0].plot(history['val_loss'],label='validation');ax[0].set(title='Loss by epoch',xlabel='Epoch',ylabel='Cross-entropy');ax[0].legend();ax[1].plot(history['accuracy'],label='train');ax[1].plot(history['val_accuracy'],label='validation');ax[1].set(title='Accuracy by epoch',xlabel='Epoch',ylabel='Accuracy');ax[1].legend();fig.tight_layout();fig.savefig(OUT/'training_curves.png',dpi=180);plt.close(fig)
    cm=confusion_matrix(truth,preds); fig,ax=plt.subplots(figsize=(8,7));sns.heatmap(cm,annot=True,fmt='d',cmap='Blues',xticklabels=LABELS,yticklabels=LABELS,ax=ax);ax.set(xlabel='Predicted',ylabel='Actual',title='Handwritten digits test confusion matrix');fig.tight_layout();fig.savefig(OUT/'confusion_matrix.png',dpi=180);plt.close(fig)
    names=['Input 1×8×8','Conv 16×8×8','Pool 16×4×4','Conv 32×4×4','Pool 32×2×2','Flatten 128','Dense 64','Dropout 0.20','Output 10']; fig,ax=plt.subplots(figsize=(10,3.5))
    for i,name in enumerate(names):
        ax.add_patch(plt.Rectangle((i,0),.88,1,facecolor=plt.cm.Blues(.25+.65*i/len(names)),edgecolor='#17324d'));ax.text(i+.44,.5,name,ha='center',va='center',fontsize=8)
        if i<len(names)-1: ax.annotate('',(i+1,.5),(i+.88,.5),arrowprops={'arrowstyle':'->','color':'#17324d'})
    ax.set_xlim(-.1,len(names));ax.set_ylim(-.15,1.15);ax.axis('off');fig.tight_layout();fig.savefig(OUT/'architecture.png',dpi=180,bbox_inches='tight');plt.close(fig)
    fig,ax=plt.subplots(3,5,figsize=(9,5));
    for a,i in zip(ax.flat,bad[:15]): a.imshow(x_test[i],cmap='gray');a.set_title(f"True {truth[i]} / Pred {preds[i]}",fontsize=8);a.axis('off')
    fig.tight_layout();fig.savefig(OUT/'misclassified_examples.png',dpi=180);plt.close(fig)
    print(json.dumps({k:metrics[k] for k in ['test_accuracy','test_macro_f1','test_weighted_f1','duration_seconds','test_n']}))
    return metrics
if __name__=='__main__': main()
