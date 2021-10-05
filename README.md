# lt2319-lab3
Test results and  problems/thoughts about the lab, e.g. how it could be improved

The Rasa model was able to handle extra words (please, etc) and some misspelt words, but for example 'South Koria' wasn't recognised. 
It wasn't a big problem since the system would just keep asking until it gets an accepted parameter.

The weather/temperature change in real time so I had to either test by interacting or update the interaction_tests_eng.txt file. 
I wonder if there's a way to use placeholders (for temperature/weather) in the interaction_tests file so we can run an automatic test like in Lab 2.

I had a problem with the system prompt in context recall:

```
S> Do you want to know the temperature or know the current weather?
U> How is the weather in Seoul? 
S> Which country?
U> What is the temperature in Seoul South Korea?
S> The temperature is 23.0°C.
U>
S> Returning to the current weather. Which city? 
```
The system asks for a different parameter when returning to the first domain, because it forgot both parameters after answering the temperature.
It could be solved by only let it forget one parameter (eg, forget country_to_search) but it would cause problem too 
if the user had asked 'What is the temperature in Osaka Japan?, then the final query would become weather in (Osaka, South Korea), since city_to_search is not forgotten.
