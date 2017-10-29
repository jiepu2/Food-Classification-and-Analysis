# Requirements

- Python	(Anaconda)	3.6.1
- anaconda 		        1.2.2
- h5py			          2.6.0
- matplotlib		      1.5.3
- numpy			          1.11.1
- requests		        2.11.1
- scikit-image		    0.12.3
- tensorflow		      1.2
- urllib3			        1.22

# Module Descriptions

Insta_images_by_loc.py is the module that harvests posts from Instagram, pre-filters food-related data, and identifies the category of the food. It reads the three coordinates lists from the csv files, and retrieve images around the reference points. You can modify the study area by giving the module a new set of reference points in a csv file. It utilises analyze1.py to interact with Microsoft Azure Computer Vision API to pre-filter the harvested dataset to keep only food-related images. Access tokens for both Instagram API and for Microsoft Azure are required for this module. You need to change the Azure access token in analyze1.py before you run this module. It also calls main.py to identify the types of food using Convolutional Neural Networks (CNN). Classes.txt is required for giving the names to the predictions. 

Analyze1.py is the module that calls Microsoft Azure Computer Vision API to pre-filter the food-related images, and to filter out unrelated images. You need to change the access token here before running. You can apply for an access token from the following link.
https://azure.microsoft.com/en-us/services/cognitive-services/computer-vision/

Main.py is the food image recognition module that identifies the types of food images. It’s using TensorFlow backend and Keras API to load our trained model – foodRec.hdf5 (not included in this Git), and to load foodRec.json. Classes.txt is also required here for mapping the predicted food category.

Geojson-mongo-import.py is for importing the suburb location data to MongoDB for geolocation calculation. It reads the location file from AUST_GEO.geojson, and writes the suburbs to MongoDB.

Pattern_analysis.py works to analyze the dietary intake pattern in Melbourne. It fetches data from MongoDB, and carries out statistics. It requires the nutrition fact data from nutritionFacts.csv and FoodInfo.csv

FF_Crawler.py is for collecting fast-food restaurants location data from Google Radar Search service.

