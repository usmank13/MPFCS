import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

my_data = np.random.rand(6500,3)  # toy 3D points
# x=my_data[:,0] 
# y=my_data[:,1] 
z_temp=my_data[:,2]
z_max = np.max(z_temp)
z_min = np.min(z_temp)
marker_data_1 = go.Scatter3d(
    x=my_data[:,0], 
    y=my_data[:,1], 
    z=my_data[:,2],
    opacity=0.6,
    mode='markers',
    marker=dict(
        size=15, #(np.max(z_temp)-np.min(z_temp))/100, 
        color= z_temp, # [np.min(z_temp), np.max(z_temp)], 
        colorscale='agsunset', 
        colorbar=dict(thickness=10,
                      len = 0.5,
                      x = 0.35,
                      y = 0.8),
        showscale=True
    )    
)

my_data = np.random.rand(6500,3)  # toy 3D points
# x=my_data[:,0] 
# y=my_data[:,1] 
z_temp=my_data[:,2]
z_max = np.max(z_temp)
z_min = np.min(z_temp)
marker_data_2 = go.Scatter3d(
    x=my_data[:,0], 
    y=my_data[:,1], 
    z=my_data[:,2],
    opacity=0.6,
    mode='markers',
    marker=dict(
        size=10, #(np.max(z_temp)-np.min(z_temp))/100, 
        color= z_temp, # [np.min(z_temp), np.max(z_temp)], 
        colorscale='pubugn', 
        colorbar=dict(thickness=10,
              len = 0.5,
              x = 0.9,
              y = 0.8), 
        showscale=True
    )    
)

my_data = np.random.rand(6500,3)  # toy 3D points
# x=my_data[:,0] 
# y=my_data[:,1] 
z_temp=my_data[:,2]
z_max = np.max(z_temp)
z_min = np.min(z_temp)
marker_data_3 = go.Scatter3d(
    x=my_data[:,0], 
    y=my_data[:,1], 
    z=my_data[:,2],
    opacity=0.6,
    mode='markers',
    marker=dict(
        size=5, #(np.max(z_temp)-np.min(z_temp))/100, 
        color= z_temp, # [np.min(z_temp), np.max(z_temp)], 
        colorscale='jet', 
        colorbar=dict(thickness=10,
                      len = 0.5,
                      x = 0.35,
                      y = 0.20),
        showscale=True
    )    
)

my_data = np.random.rand(6500,3)  # toy 3D points
# x=my_data[:,0] 
# y=my_data[:,1] 
z_temp=my_data[:,2]
z_max = np.max(z_temp)
z_min = np.min(z_temp)
marker_data_4 = go.Scatter3d(
    x=my_data[:,0], 
    y=my_data[:,1], 
    z=my_data[:,2],
    opacity=0.6,
    mode='markers',
    marker=dict(
        size=3, #(np.max(z_temp)-np.min(z_temp))/100, 
        color= z_temp, # [np.min(z_temp), np.max(z_temp)], 
        colorscale='viridis', 
        colorbar=dict(thickness=10,
                      len = 0.5,
                      x = 0.9,
                      y = 0.2), 
        showscale=True,
    )    
)

import plotly.graph_objects as go

fig = go.FigureWidget(make_subplots(rows=2, cols=2,
                    specs=[[{'type': 'scene'}, {'type': 'scene'}],
           [{'type': 'scene'}, {'type': 'scene'}]]))

fig.add_trace(marker_data_1, row=1, col=1)
fig.add_trace(marker_data_2, row=1, col=2)
fig.add_trace(marker_data_3, row=2, col=1)
fig.add_trace(marker_data_4, row=2, col=2)


fig.update_layout(height=700, showlegend=False)
fig

