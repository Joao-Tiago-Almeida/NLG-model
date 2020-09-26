# NLG-model

Natural Language Generation model which produces a report from a formatted input as excel or tableau.
The input is a table whether excel or tableau and it is used [pandas.DataFrame](https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.html) to access to the data and produces a final report.

## Pratical Example

[Input](https://public.tableau.com/views/RegionalSampleWorkbook/Storms?:embed=y&:showVizHome=n&:jsdebug=y&:bootstrapWhenNotified=y&:tabs=n&:apiID=handler0)  | [Output](https://joao-tiago-almeida.github.io/NLG-model/)
------------- | -------------
![input](https://user-images.githubusercontent.com/39059647/94350049-52af6500-0042-11eb-94f9-f6037ee6a8b0.png)| ![output](https://user-images.githubusercontent.com/39059647/94350048-5216ce80-0042-11eb-91e7-9f8e4caf6542.png) 

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

### Prerequisites

To worked in this project, it was used python3 (3.8.4)


### Installing

Get pip3:
```
python3 get-pip.py
```
Get technologies
```
pip3 install Flask
pip3 install openpyxl
pip3 install excel2img
pip3 install elasticsearch
pip3 install nltk
pip3 install wordnet
pip3 install matplotlib
pip3 install numpy
pip3 install pandas
pip3 install sklearn
```

## Running the tests

Here is more Tableaus which the model produces nice reports:
- https://public.tableau.com/views/money1_13/CashInstruments?:embed=y&:display_count=y&:origin=viz_share_link
- https://public.tableau.com/profile/venkat8761#!/vizhome/worldCovid-19/Covid-19
- https://public.tableau.com/views/RegisteredVehiclesOpenDataProject/BrandBenchmark?:showVizHome=n&amp;:embed=t
- https://public.tableau.com/views/ThePulpFictionConnection/PulpFictionConnection?:showVizHome=n&amp;:embed=t
- https://public.tableau.com/views/CashlessSociety/CashlessSociety?:showVizHome=n&amp;:embed=t
- https://public.tableau.com/en-us/gallery/costs-using-car?tab=viz-of-the-day&type=viz-of-the-day
- https://public.tableau.com/views/Womensrepresentationinpoliticsvizforsocialgood/WomeninPolitics?:showVizHome=n&amp;:embed=t
- https://public.tableau.com/views/TopLinkedInSkillsfor20142015and2016/LinkedInDashboard?:showVizHome=n&amp;:embed=t
- https://public.tableau.com/views/BigBookofLineCharts/BBLC1?:showVizHome=n&amp;:embed=t
- https://public.tableau.com/views/TheMeatMap/meat-dash?:showVizHome=n&amp;:embed=t
- https://public.tableau.com/views/2018W27NewYorkRatSightings/NewYorkRatSightings?:showVizHome=n&amp;:embed=t

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgment

I worked two months in this NLG model during my Summer Intership at Syone at 2020.
