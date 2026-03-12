###Prototype Description

This prototype demonstrates a WiFi signal monitoring and visualization system designed for indoor environments such as offices or large buildings. The system simulates wireless signals from multiple access points and analyzes their coverage across a building floor map.

A headless GNU Radio-based signal generator produces signal strength values for three simulated antennas (AP1, AP2, and AP3). These values are periodically written to a shared data file. A separate Python-based visualization module reads the signal data in real time and computes signal propagation across the building layout using a distance-based attenuation model.

The visualization module overlays a dynamically generated heatmap on top of a floor plan image, showing strong signal regions, weak coverage areas, and potential dead zones. An optional jammer simulation can also introduce interference, allowing the system to demonstrate how signal degradation may appear in the coverage map.

This prototype illustrates the core idea of combining signal generation, real-time monitoring, and spatial visualization to assist network administrators in understanding wireless coverage and identifying areas where signal quality may be poor or interference may occur.
