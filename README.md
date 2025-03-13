Data for the Paper "Parsing Graphical Summaries from Argumentative Dialogues", Clayton, Damonte and Gaizauskas, 2024

Data is derived from Debatabase (idebate.net) - to be used for noncommercial academic purposes

(Copyright © 2005 International Debate Education Association. All Rights Reserved). 



Usage:

"Data" contains 6 files, the "multilevel" data separated into train/val/test, and non-multilevel data separated into train/val/test
The data in the multilevel and non-multilevel files is the same, except that the multilevel data contains comments attacking/ supporting other comments, 
while in the non-mulitlevel data, all comments attack or support the "main topic".

To inspect the data, we first need to install three packages, then run the load_data.py script:

pip install arglu networkx pandas

python load_data.py