import os
import vtk
import qt
import ctk
import slicer
from slicer import util
import MakeModelEffect, EditUtil
from EditOptions import HelpButton
from EditUtil import EditUtil
import Effect
import time

###Run in the Slicer program with the execfile() command


##make sure the ThresholdEffect and MakeModelEffect and all required dependencies are in the location where python
##looks for modules from Slicer

#Set folder path and filename
##for windows
##    PATH_TO_WORKING_DIR = "C:\\Users\\DB\\Desktop\\"
	
##for linux
PATH_TO_WORKING_DIR = "/home/djbranglab-user/Desktop/slicer_scripting/test_dir/"    

list_of_files = []
for file in os.listdir(PATH_TO_WORKING_DIR):
    if file.endswith(".gz") or file.endswith(".nii"):
        list_of_files.append(str(file))

#create list of the model nodes being created to save at the end
list_of_model_nodes = []
for each_file in list_of_files:
	if ".nii.gz" in each_file:
		short_name = each_file[:-7]
	elif ".nii" in each_file:
		short_name = each_file[:-4]

	print short_name
	#returns tuple.  ex: (True, (vtkMRMLScalarVolumeNode)0x7f92a35c74d0)
	#get the node that represents the volume
	my_node = slicer.util.loadVolume(PATH_TO_WORKING_DIR + each_file, returnNode = True)

	#center the volume
	slicer.modules.volumes.logic().CenterVolume(my_node[1])

	#create a label map
	#Automates the processing that happens when the following dialog box appears:
	##create a merge label map or a segmentation for a selected master volume VOLUMENAME.amyg
	###New volume will be VOLUMENAME.amyg-label
	###Select the color table node that will be used for segmentation labels
	label = slicer.modules.volumes.logic().CreateAndAddLabelVolume(my_node[1], short_name + "-label") 
	label.GetDisplayNode().SetAndObserveColorNodeID('vtkMRMLColorTableNodeFileGenericAnatomyColors.txt') 
	qt.QApplication.processEvents() 

	#select the editor module
	#i don't think we need to do this, but saving to make sure
	slicer.util.selectModule("Editor")
	slicer.modules.EditorWidget.helper.setVolumes(my_node[1],label)
	qt.QApplication.processEvents() 

	#thresholding
	thresh = vtk.vtkImageThreshold()
	thresh.SetInputData( my_node[1].GetImageData())

	#Set threshold using default values from GUI
	lo, hi = my_node[1].GetImageData().GetScalarRange()
	#Make sure something was returned.  Lo will often return 0 (which == false)
	#so hi value is used as the test.
	if hi:
		lo = lo + (0.25 * (hi-lo))
	thresh.ThresholdBetween(lo, hi)
	thresh.SetInValue( EditUtil().getLabel())
	thresh.SetOutValue( 0 )
	thresh.SetOutputScalarType( label.GetImageData().GetScalarType())
	thresh.Update()

	##not really sure what next two do but it appears to save the changes made with threshold
	label.GetImageData().DeepCopy( thresh.GetOutput() )
	EditUtil.markVolumeNodeAsModified(label)
	
	my_node[1].Modified()
	label.Modified()
	#
	qt.QApplication.processEvents() 

	slicer.modules.EditorWidget.helper.setVolumes(my_node[1],label)
	##Make Model Effect

	time.sleep(5)
	result = MakeModelEffect.MakeModelEffectLogic(Effect.EffectLogic).makeModel(modelName=short_name + "_model")

	my_node[1].Modified()
	label.Modified()

	#if result == None:
	#	print "could not create model for " + short_name
	#else:
	#	list_of_model_nodes.append(short_name)
	list_of_model_nodes.append(short_name)

	#save node as .stl
	#need to load file back in as a volume or it will be black and white instead of green
	#probably need to save the model node as vtkMRMLScalarVolumeNode
	
	qt.QApplication.processEvents()
	slicer.app.processEvents()