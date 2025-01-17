import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix
from sklearn.utils.multiclass import unique_labels

# assumed to be numpy
def std(array):	
	array = np.where(array>180,360-array,array)
	return np.std(array)

def plot_confusion_matrix(y_pred, y_true, classes,
						  normalize=False,
						  title=None,
						  cmap=plt.cm.Blues):
	
	title = 'Confusion matrix'

	# Compute confusion matrix
	cm = confusion_matrix(y_true, y_pred)
	# Only use the labels that appear in the data
	classes = classes[unique_labels(y_true, y_pred)]

	fig, ax = plt.subplots()
	im = ax.imshow(cm, interpolation='nearest', cmap=cmap)
	ax.figure.colorbar(im, ax=ax)
	# We want to show all ticks...
	step = 1 if cm.shape[0]<=10 else cm.shape[0]//10
	ticks = np.arange(0,cm.shape[0],step)#*int(360/min(cm.shape[0],10))
	ax.set(title=title,
			ylabel='True label',
			xlabel='Predicted label')

	# Rotate the tick labels and set their alignment.
	plt.setp(ax.get_xticklabels(), rotation=45, ha="right",
			 rotation_mode="anchor")

	# print quantity in each block, only for few classes bc gets cluttered
	if(len(classes)<10):
		fmt = '.2f' if normalize else 'd'
		thresh = cm.max() / 2.
		for i in range(cm.shape[0]):
			for j in range(cm.shape[1]):
				ax.text(j, i, format(cm[i, j], fmt),
						ha="center", va="center",
						color="white" if cm[i, j] > thresh else "black")
	fig.tight_layout()
	return ax


def test_stats(args, all_pred, all_targ, all_diff):
	# ===============================================
	# print basic statistics
	print("For 360 degrees:")
	print("mean:",np.mean(all_diff))
	print("standard deviation:",np.std(all_diff))
	print("median:",np.median(all_diff))

	# ===============================================
	# plot confusion matrix plot
	
	print("max:",max(all_pred))

	print("class k>5:",len(np.where(all_diff>5)[0]),'/',len(all_diff))
	# print("reg   k>5:",len(np.where(all_diff_reg>5)[0]),'/',len(all_diff_reg))

	

	classes = np.arange(0,max(max(all_pred),max(all_targ))+1)
	trig = 'Trig Component ' if args.separate_trig and args.type=='regression' else ''
	if(args.type=='classification' and not args.hierarchy):
		trig = str(args.nClasses)+' '
	plot_confusion_matrix(all_pred.astype(np.int32), all_targ.astype(np.int32), classes)
	plt.title(("{} {}Error - ".format(args.type.title(),trig)+str(args.animal).title()))
	plt.xlabel("True Label")
	plt.ylabel("Predicted Label")
	plt.show()

	# print(list(all_diff))

	# ===============================================
	# Plot error histogram
	bins_def = np.arange(max(360,np.max(all_diff)))
	# hist,bins = np.histogram(all_diff,bins = bins_def)
	# plt.text(100,50,'mean: {:3f}\nmedian: {:3f}'.format(np.mean(all_diff),np.median(all_diff)))
	
	hist,bins = np.histogram(all_diff,bins = bins_def)

	f, (ax,ax2) = plt.subplots(2, 1, sharex=True)
	ax.hist(all_diff,bins_def)
	ax2.hist(all_diff,bins_def)
	ax.set_ylim(max(hist)-max(hist)*.2, max(hist)+max(hist)*.1)
	ax2.set_ylim(0, max(hist)*.2)
	ax2.legend().set_visible(False)

	ax.spines['bottom'].set_visible(False)
	ax2.spines['top'].set_visible(False)
	ax.xaxis.tick_top()
	ax.tick_params(labeltop='off')
	ax2.xaxis.tick_bottom()
	d = .015
	kwargs = dict(transform=ax.transAxes, color='k', clip_on=False)
	ax.plot((-d,+d),(-d,+d), **kwargs)
	ax.plot((1-d,1+d),(-d,+d), **kwargs)
	kwargs.update(transform=ax2.transAxes)
	ax2.plot((-d,+d),(1-d,1+d), **kwargs)
	ax2.plot((1-d,1+d),(1-d,1+d), **kwargs)

	# plt.hist(all_diff,bins_def)
	t = '{} {}Error - '.format(args.type.title(),trig)+str(args.animal).title()
	ax.set_title(t)
	plt.xlabel('Difference Between Predicted and True Labels')
	# plt.ylabel('Frequency in Test Set')
	f.text(0.04, 0.5, 'Frequency in Test Set', va='center', rotation='vertical')
	plt.show()

	# ===============================================
	# histogram of frequency below some difference thresh
	# x = np.array([554,296,150,71,37,23,17,16])
	# x1=[541, 580, 570, 555, 543, 529, 568, 553]
	# x2=[306, 298, 289, 306, 284, 286, 302, 301]
	# x3 = [146, 141, 157, 167, 148, 146, 148, 148]
	# x4 = [64, 70, 76, 69, 82, 67, 70, 70]
	# x5 = [29, 42, 36, 30, 37, 52, 40, 37]
	# x6 = [20, 26, 25, 26, 24, 24, 21, 23]
	# x7 = [25, 17, 18, 14, 15, 18, 16, 13]
	# x8 = [15, 18, 15, 13, 22, 11, 21, 23]
	# x25 = [8, 5, 7, 7, 8, 8, 8, 6]

	# plt.bar(np.arange(8), x)
	# plt.title('{} {}Error - '.format(args.type.title(),trig)+str(args.animal).title())
	# plt.xlabel('Max Angle Difference Threshold ')
	# plt.ylabel('Number of Differences Less Than Threshold')
	# plt.show()


	# ===============================================
	# distribution of error and label
	

	# ===============================================
	# find worst errors and save them


def test_stats_hierarchy(args, all_pred, all_targ, all_diff, all_pred_reg, all_targ_reg, all_diff_reg):
	# ===============================================
	# print basic statistics
	print("Classification:")
	print("mean:",np.mean(all_diff))
	print("standard deviation:",np.std(all_diff))
	print("median:",np.median(all_diff))
	print("max:",max(all_pred))

	print("Regression:")
	print("mean:",np.mean(all_diff_reg))
	print("standard deviation:",np.std(all_diff_reg))
	print("median:",np.median(all_diff_reg))
	print("max:",max(all_pred_reg))

	print("class k>5:",len(np.where(all_diff>5)[0]),'/',len(all_diff))
	print("reg   k>5:",len(np.where(all_diff_reg>5)[0]),'/',len(all_diff_reg))


	# ===============================================
	# plot confusion matrix plot
	
	
	

	classes = np.arange(0,max(max(all_pred),max(all_targ))+1)
	trig = 'Trig Component ' if args.separate_trig and args.type=='regression' else ''
	if(args.type=='classification' and not args.hierarchy):
		trig = str(args.nClasses)+' '
	plot_confusion_matrix(all_pred.astype(np.int32), all_targ.astype(np.int32), classes)
	plt.title(("Hierarchy Classification ({} Class) Error - ".format(args.nClasses)+str(args.animal).title()))
	plt.xlabel("True Label")
	plt.ylabel("Predicted Label")
	plt.show()

	classes = np.arange(0,max(max(all_pred_reg),max(all_targ_reg))+1)
	trig = 'Trig Component ' if args.separate_trig and args.type=='regression' else ''
	if(args.type=='classification' and not args.hierarchy):
		trig = str(args.nClasses)+' '
	plot_confusion_matrix(all_pred_reg.astype(np.int32), all_targ_reg.astype(np.int32), classes)
	plt.title(("Hierarchy Regression ({} Class) Error - ".format(args.nClasses)+str(args.animal).title()))
	plt.xlabel("True Label")
	plt.ylabel("Predicted Label")
	plt.show()


	# ===============================================
	# Plot error histogram
	bins_def = np.arange(max(360,np.max(all_diff_reg)))
	# hist,bins = np.histogram(all_diff_reg,bins = bins_def)
	# plt.text(100,50,'mean: {:3f}\nmedian: {:3f}'.format(np.mean(all_diff_reg),np.median(all_diff_reg)))
	
	hist,bins = np.histogram(all_diff_reg,bins = bins_def)

	f, (ax,ax2) = plt.subplots(2, 1, sharex=True)
	ax.hist(all_diff_reg,bins_def)
	ax2.hist(all_diff_reg,bins_def)
	ax.set_ylim(max(hist)-max(hist)*.2, max(hist)+max(hist)*.1)
	ax2.set_ylim(0, max(hist)*.2)
	ax2.legend().set_visible(False)

	ax.spines['bottom'].set_visible(False)
	ax2.spines['top'].set_visible(False)
	ax.xaxis.tick_top()
	ax.tick_params(labeltop='off')
	ax2.xaxis.tick_bottom()
	d = .015
	kwargs = dict(transform=ax.transAxes, color='k', clip_on=False)
	ax.plot((-d,+d),(-d,+d), **kwargs)
	ax.plot((1-d,1+d),(-d,+d), **kwargs)
	kwargs.update(transform=ax2.transAxes)
	ax2.plot((-d,+d),(1-d,1+d), **kwargs)
	ax2.plot((1-d,1+d),(1-d,1+d), **kwargs)

	t = 'Hierarchy Regression Error - '+str(args.animal).title()
	ax.set_title(t)
	plt.xlabel('Difference Between Predicted and True Labels')
	f.text(0.04, 0.5, 'Frequency in Test Set', va='center', rotation='vertical')
	plt.show()

	



