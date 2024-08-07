import os
import json
import plotly.graph_objects as go
import plotly.io as pio

def plot_jsons():
    # Directory containing JSON files
    json_dir = '/home/undadmin/Documents/GitHub/BEV_localization/fourier_template_matching/output/jsons/'  # replace with your directory path
    output_dir = '/home/undadmin/Documents/GitHub/BEV_localization/fourier_template_matching/output/plots/plots_html'  # replace with your desired output directory

    # Create the output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # List all JSON files in the directory
    json_files = [f for f in os.listdir(json_dir) if f.endswith('.json')]

    # Loop through each JSON file
    for json_file in json_files:
        json_path = os.path.join(json_dir, json_file)
        
        # Load JSON data from file
        with open(json_path, 'r') as file:
            data = json.load(file)
        
        # Extract keys and values
        blur_levels = list(data.keys())
        total_correct_matches = [(item[0] / 1000) for item in data.values()]
        correct_at_one = [(item[1] / 1000) for item in data.values()]
        correct_at_two = [(item[2] / 1000) for item in data.values()]
        correct_at_three = [(item[3] / 1000) for item in data.values()]
        
        # Create Plotly figure
        fig = go.Figure()

        # Add traces for each metric, all starting from the same baseline (0)
        fig.add_trace(go.Bar(x=blur_levels, y=total_correct_matches, name='Total Correct Matches'))
        fig.add_trace(go.Bar(x=blur_levels, y=correct_at_one, name='Correct at One'))
        fig.add_trace(go.Bar(x=blur_levels, y=correct_at_two, name='Correct at Two'))
        fig.add_trace(go.Bar(x=blur_levels, y=correct_at_three, name='Correct at Three'))
        
        # Update layout
        fig.update_layout(
            title=f'Correct Matches by Blur Level - {json_file}',
            xaxis_title='Blur Level',
            yaxis_title='Percentage Correct Matches',
            barmode='overlay'  # Set to 'overlay' to overlay bars on top of each other
        )
        
        # Save the figure as an HTML file
        output_path = os.path.join(output_dir, f'{os.path.splitext(json_file)[0]}.html')
        pio.write_html(fig, file=output_path, auto_open=False)
        
        print(f"The plot for {json_file} has been saved to {output_path}")

    print("All plots have been processed and saved.")

if __name__ == '__main__':
    plot_jsons()