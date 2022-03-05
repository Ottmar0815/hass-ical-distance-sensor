# hass-ical-distance-sensor
iCalender Entfernungssensor für Home Assistant

Willkomemn zum hass-ical-distance-sensor!

Problemstellung:
Im Heimbereich wird eine Photovoltaikanlage genutzt und ein Eletro-Auto soll damit geladen werden.
Bei einer Wallbox kann eine Mindest-Reichweite eingestellt werden die aber aus dem öffentlichen Netz bezogen wird und damit teurer als durch Eigenstrom-Nutzung.
Um aber den Speicher im Auto für den Solar-Strom effizienter nutzen zu können sollte er nur so wenig wie möglich aber so viel wie nötig aus dem Netz geladen werden.

Lösung:
In einem Kalender kann der Bedarf an Mobilität in Form von Terminen geführt werden.
Das Skript ermittelt die Reichweite für den folgenden Tag und stellt diese im Home Assistant bereit, wo es dann weiter verarbeit werden kann.

In Home Assistant kann über den command_line-sensor das Python-Skript aufgerufen werden.
Ein configuration.yaml-Beispiel liegt im Repository bei.

Das Skript muss mit einer Konfiguration-Datei als Parameter aufgerufen werden.

Als Basis dient eine iCalendar-Datei die über einen Link öffentlich erreichbar sein muss.
Aus dem Kalender werden von den Terminen die Ortsangabe entnommen und die Entfernung in Kilometern für eine Hin- und Rückfahrt berechnet.
Diese Daten werden über die API von [Geoapify.com](https://www.geoapify.com) abgeholt. Es ist daher notwendig einen Account auf der Webseite anzulegen und eine API-Key zu erstellen. Dieser muss dann in der Konfiguration-Datei angegeben werden.

Es werden nur Termine berücksichtigt die am heutigen Tag stattfinden und in der Zukunft liegen.
Es gibt eine "Tageswechsel"-Einstellung nach fester Uhrzeit oder über den Sonnenuntergang. Ist dieser Zeitpunkt überschritten wird der Folgetag mitgerechnet.
