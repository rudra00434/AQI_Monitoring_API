# AQI_Monitoring_API
It is a Flask based REST api for calculating Air quality index in real time 

# Test with cURL or Postman :
```
curl -X POST http://127.0.0.1:5000/api/v1/aqi \
-H "Content-Type: application/json" \
-d '{"pm25":45, "co2":700, "humidity":60, "temperature":30}'
```
# Example use of cURL for Iot projects :
```
curl -X GET https://api.openweathermap.org/data/2.5/weather?q=Kolkata
```
