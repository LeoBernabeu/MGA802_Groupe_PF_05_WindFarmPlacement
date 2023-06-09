#!/bin/bash

period=($1)
current_year=$(date | awk -F ' ' '{print $4}')
list_id=$(awk -F ',' '{print $4 $12 $13}' Station_Inventory_EN.csv)
i=0
for station in ${list_id};
do
  ((i++))
  echo ${i}  # Juste pour suivre l'avancement
  data=($(echo ${station} | grep -Eo "[[:digit:]]+")) # data = [id, start_year, end_year]
  if [[ -n ${data} ]];
  then
    if [[ ${data[2]} > $((current_year-period)) ]];
    then
      mkdir -p data/${data[0]}
      for ((year=$((current_year-period)); year<=${data[2]}; year++))
      do
        if [[ ! (-d data/${data[0]}/${year}) ]]; # Si le dossier de l'année existe déjà c'est qu'on la déjà traité
        then
          mkdir -p data/${data[0]}/${year}/Daily
          mkdir -p data/${data[0]}/${year}/Hourly
          for month in `seq 1 12`;
          do
            curl -# --get https://climate.weather.gc.ca/climate_data/bulk_data_e.html?format=csv \
            -d stationID=${data[0]} \
            -d Year=${year} \
            -d Month=${month} \
            -d timeframe=1 \
            -d submit=Download+Data \
            --output data/${data[0]}/${year}/Hourly/${month}.csv

            curl --get https://climate.weather.gc.ca/climate_data/bulk_data_e.html?format=csv \
            -d stationID=${data[0]} \
            -d Year=${year} \
            -d Month=${month} \
            -d timeframe=2 \
            -d submit=Download+Data \
            --output data/${data[0]}/${year}/Daily/${month}.csv
          done
        fi
      done
    fi
  fi
done