import json

# Set up the input file
input_file_name = 'output.json'

# Set up the output file
output_file_name = 'output.html'

def main():
    # Read the input file
    with open(input_file_name, 'r') as input_file:
        input_data = json.load(input_file)

    # Set up the HTML output
    html_output = ''

    # Process the elements
    for element in input_data['elements']:
        if element['type'] == 'heading':
            html_output += f'<h{element["level"]}>{element["text"]}</h{element["level"]}>'
        elif element['type'] == 'paragraph':
            html_output += f'<p>{element["text"]}</p>'
        elif element['type'] == 'table':
            html_output += '<table>'
            html_output += '<thead><tr>'
            for header_cell in element['headerRow']:
                html_output += f'<th>{header_cell["text"]}</th>'
            html_output += '</tr></thead>'
            html_output += '<tbody>'
            for body_row in element['bodyRows']:
                html_output += '<tr>'
                for body_cell in body_row:
                    html_output += f'<td>{body_cell["text"]}</td>'
                html_output += '</tr>'
            html_output += '</tbody>'
            html_output += '</table>'

    # Write the output file
    with open(output_file_name, 'w') as output_file:
        output_file.write(html_output)
    print(f'Wrote output to {output_file_name}')
