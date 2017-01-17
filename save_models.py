for each_node in list_of_model_nodes:
	result = slicer.util.saveNode(slicer.mrmlScene.GetFirstNodeByName(each_node + "_model"), PATH_TO_WORKING_DIR + each_node + ".stl")
	if result == True:
		print each_node + " saved"
	else:
		print each_node + " did not save"