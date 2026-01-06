import xml.etree.ElementTree as ET
from xml.dom import minidom
import sys

def format_duration(duration_elem):
    """Format duration from XML elements to seconds with 2 decimal places"""
    try:
        hh = int(duration_elem.find('HH').text)
        mm = int(duration_elem.find('MM').text)
        ss = int(duration_elem.find('SS').text)
        ms = int(duration_elem.find('MS').text)
        total_seconds = hh * 3600 + mm * 60 + ss + ms / 1000.0
        return f"{total_seconds:.2f}"
    except (AttributeError, ValueError):
        return "0.00"

def get_test_duration(test_elem):
    """Get formatted duration for a test"""
    time_elem = test_elem.find('Time')
    if time_elem is not None:
        duration_elem = time_elem.find('Duration')
        if duration_elem is not None:
            return format_duration(duration_elem)
    return "0.00"

def get_test_name(test_elem):
    """Get test name, preferring ExtendedName if available"""
    extended_name = test_elem.find('ExtendedName')
    if extended_name is not None and extended_name.text:
        return extended_name.text
    name = test_elem.find('Name')
    if name is not None and name.text:
        return name.text
    return "Unknown Test"

def get_test_status(test_elem):
    """Get test status (PASS/FAIL) with color coding"""
    pass_fail = test_elem.find('PassFail')
    if pass_fail is not None:
        di = pass_fail.find('DI')
        if di is not None:
            value = di.find('V')
            if value is not None:
                status = value.text
                if status == 'PASS':
                    return '<span style="color:#00CC00">PASS</span>'
                elif status == 'FAIL':
                    return '<span style="color:red">FAIL</span>'
                else:
                    return status
    return 'UNKNOWN'

def format_time_element(time_elem):
    """Format time element as HH:MM:SS"""
    try:
        hh = time_elem.find('HH').text.zfill(2)
        mm = time_elem.find('MM').text.zfill(2)
        ss = time_elem.find('SS').text.zfill(2)
        return f"{hh}:{mm}:{ss}"
    except AttributeError:
        return "--:--:--"

def get_collection_duration(collection_elem):
    """Get formatted duration for the entire test collection"""
    time_elem = collection_elem.find('Time')
    if time_elem is not None:
        duration_elem = time_elem.find('Duration')
        if duration_elem is not None:
            return format_duration(duration_elem)
    return "0.00"

def get_collection_time_info(collection_elem):
    """Get formatted start and stop times for the collection"""
    start_time = "--:--:--"
    stop_time = "--:--:--"
    duration = "0.00"
    
    time_elem = collection_elem.find('Time')
    if time_elem is not None:
        start_elem = time_elem.find('Start')
        stop_elem = time_elem.find('Stop')
        duration_elem = time_elem.find('Duration')
        
        if start_elem is not None:
            start_time = format_time_element(start_elem)
        if stop_elem is not None:
            stop_time = format_time_element(stop_elem)
        if duration_elem is not None:
            duration = format_duration(duration_elem)
    
    return start_time, stop_time, duration

def get_date_info(collection_elem):
    """Get formatted date as MM/DD/YYYY"""
    date_elem = collection_elem.find('Date')
    if date_elem is not None:
        try:
            mm = date_elem.find('MM').text.zfill(2)
            dd = date_elem.find('DD').text.zfill(2)
            yyyy = date_elem.find('YYYY').text
            return f"{mm}/{dd}/{yyyy}"
        except AttributeError:
            pass
    return "--/--/----"

def get_tester_info(collection_elem):
    """Get tester information"""
    tester_info = {
        'name': '',
        'type': '',
        'equipment': [],
        'pc_config': [],
        'sw_config': []
    }
    
    tester_elem = collection_elem.find('Tester')
    if tester_elem is not None:
        # Get tester name and type
        name_elem = tester_elem.find('Name')
        if name_elem is not None and name_elem.text:
            tester_info['name'] = name_elem.text
            
        type_elem = tester_elem.find('Type')
        if type_elem is not None and type_elem.text:
            tester_info['type'] = type_elem.text
        
        # Get equipment configuration
        equip_elem = tester_elem.find('EquipmentConfig')
        if equip_elem is not None:
            for di in equip_elem.findall('DI'):
                n_elem = di.find('N')
                v_elem = di.find('V')
                if n_elem is not None and v_elem is not None:
                    tester_info['equipment'].append((n_elem.text, v_elem.text))
        
        # Get PC configuration
        pc_config_elem = tester_elem.find('PCConfig')
        if pc_config_elem is not None:
            for di in pc_config_elem.findall('DI'):
                n_elem = di.find('N')
                v_elem = di.find('V')
                if n_elem is not None and v_elem is not None:
                    tester_info['pc_config'].append((n_elem.text, v_elem.text))
        
        # Get software configuration
        sw_config_elem = tester_elem.find('SWConfigInfo')
        if sw_config_elem is not None:
            versions_elem = sw_config_elem.find('Versions')
            if versions_elem is not None:
                for di in versions_elem.findall('DI'):
                    n_elem = di.find('N')
                    v_elem = di.find('V')
                    if n_elem is not None and v_elem is not None:
                        tester_info['sw_config'].append((n_elem.text, v_elem.text))
    
    return tester_info

def get_dataset_info(test_elem):
    """Get dataset information for a test"""
    datasets = []
    
    # Get all DataSetCollection elements
    for dsc in test_elem.findall('DataSetCollection'):
        dataset_info = {
            'name': '',
            'input_headers': [],
            'input_values': [],
            'output_headers': [],
            'output_values': [],
            'times': []
        }
        
        # Get dataset collection name
        name_elem = dsc.find('Name')
        if name_elem is not None and name_elem.text:
            dataset_info['name'] = name_elem.text
        
        # Process each DataSet
        for dataset in dsc.findall('DataSet'):
            # Get input data
            inputs_elem = dataset.find('Inputs')
            if inputs_elem is not None:
                input_row = []
                for di in inputs_elem.findall('DI'):
                    n_elem = di.find('N')
                    v_elem = di.find('V')
                    u_elem = di.find('U')
                    
                    if n_elem is not None:
                        header = n_elem.text
                        if u_elem is not None and u_elem.text:
                            header += f" ({u_elem.text})"
                        if header not in dataset_info['input_headers']:
                            dataset_info['input_headers'].append(header)
                    
                    if v_elem is not None:
                        input_row.append(v_elem.text)
                    else:
                        input_row.append('')
                
                # Pad input_row to match header count
                while len(input_row) < len(dataset_info['input_headers']):
                    input_row.append('')
                
                dataset_info['input_values'].append(input_row)
            
            # Get output data
            outputs_elem = dataset.find('Outputs')
            if outputs_elem is not None:
                output_row = []
                
                # Handle Result elements in Outputs
                for result in outputs_elem.findall('Result'):
                    di = result.find('DI')
                    if di is not None:
                        n_elem = di.find('N')
                        v_elem = di.find('V')
                        
                        if n_elem is not None:
                            header = n_elem.text
                            if header not in dataset_info['output_headers']:
                                dataset_info['output_headers'].append(header)
                        
                        if v_elem is not None:
                            output_row.append(v_elem.text)
                        else:
                            output_row.append('')
                
                # Handle Limits if present
                for result in outputs_elem.findall('Result'):
                    limits = result.find('Limits')
                    if limits is not None:
                        min_elem = limits.find('Min')
                        if min_elem is not None:
                            header = f"{result.find('DI').find('N').text} Min" if result.find('DI') is not None and result.find('DI').find('N') is not None else "Min"
                            if header not in dataset_info['output_headers']:
                                dataset_info['output_headers'].append(header)
                            output_row.append(min_elem.text)
                
                # Pad output_row to match header count
                while len(output_row) < len(dataset_info['output_headers']):
                    output_row.append('')
                
                dataset_info['output_values'].append(output_row)
            
            # Get time data
            ts = dataset.get('ts', '')
            dur = dataset.get('dur', '')
            if ts or dur:
                dataset_info['times'].append((ts, dur))
        
        datasets.append(dataset_info)
    
    return datasets

def generate_html_header(collection_name, date_info):
    """Generate HTML header section"""
    html = '''<!DOCTYPE html>
<html>
<head>
<STYLE TYPE="text/css">
      body {
      font-family: Sans-Serif;
      }
      table { empty-cells:show; border-collapse:collapse; border-style: solid; border-color: gray; font-size: 10pt;}
      #ttfmt { border-style: none; font-size: 8pt;}
      th,td {
      padding-left: 5px;
      padding-right: 5px;
      padding-top: 1px;
      padding-bottom: 1px;
      }
</STYLE>
</head>
<body>
'''
    
    html += f'<HR COLOR="#6699CC" SIZE="10"><big><big><big><b>Test Report:  {collection_name}</b></big></big></big><br><br>'
    html += '<big><b>UUT ID:  </b></big><br>'
    html += f'<b>Date:  {date_info}</b><br><br>'
    
    return html

def generate_toc(merged_tests):
    """Generate table of contents"""
    html = '<a name="TOC"></a><HR COLOR="#6699CC" SIZE="2"><big><big><b>Table of Contents</b></big></big>'
    html += '<UL><table border="1"><tr>'
    html += '<td bgcolor="#CCCCCC"><b>Test Name</b></td>'
    html += '<td bgcolor="#CCCCCC"><b>Status</b></td>'
    html += '<td bgcolor="#CCCCCC"><b>Duration (s)</b></td></tr>'
    
    for i, (test_key, test_data) in enumerate(merged_tests.items(), 1):
        test_name = test_data['name']
        status = test_data['status']
        duration = test_data['duration']
        
        # Clean up status for TOC display
        status_text = status.replace('<span style="color:#00CC00">', '').replace('</span>', '').replace('<span style="color:red">', '')
        
        html += f'<tr><td><a href="#_{i}">{test_name}</a></td>'
        
        # Add color coding for status
        if 'PASS' in status_text:
            html += '<td bgcolor="#00CC00">PASS</td>'
        elif 'FAIL' in status_text:
            html += '<td bgcolor="red">FAIL</td>'
        else:
            html += f'<td>{status_text}</td>'
            
        html += f'<td>{duration}</td></tr>'
    
    html += '</table></UL>'
    return html

def generate_collection_info(collection_elem):
    """Generate collection information section"""
    start_time, stop_time, duration = get_collection_time_info(collection_elem)
    tester_info = get_tester_info(collection_elem)
    
    html = '<table id="ttfmt"><tr><td><UL><b>Additional Test Run Data</b>'
    
    # Time information
    html += '<UL><LI>Test Time...<UL>'
    html += f'<LI>Start Time:  {start_time}</LI>'
    html += f'<LI>Stop Time:  {stop_time}</LI>'
    html += f'<LI>Duration:  {duration}s</LI></UL></LI></UL>'
    
    # UUT Information
    html += '<UL><LI><span>UUT Information...</span><UL>'
    html += '<LI>UUT ID:  </LI></UL></LI></UL>'
    
    # XTT Information
    html += '<UL><LI><span>XTT Information...</span><UL>'
    html += '<LI>XTT :  </LI></UL></LI></UL>'
    
    # Test Station Information
    html += '<UL><LI><span>Test Station Information...</span><UL>'
    html += f'<LI>Name:  {tester_info["name"]}</LI>'
    html += f'<LI>Type:  {tester_info["type"]}</LI>'
    
    # Equipment Configuration
    if tester_info['equipment']:
        html += '<LI><span>Equipment Configuration...</span><UL>'
        for name, value in tester_info['equipment']:
            html += f'<LI>{name}:  {value}</LI>'
        html += '</UL></LI>'
    
    # PC Configuration
    if tester_info['pc_config']:
        html += '<LI><span>PC Configuration...</span><UL>'
        for name, value in tester_info['pc_config']:
            html += f'<LI>{name}:  {value}</LI>'
        html += '</UL></LI>'
    
    # Software Configuration
    if tester_info['sw_config']:
        html += '<LI><span>Software Configuration...</span><UL>'
        for name, value in tester_info['sw_config']:
            html += f'<LI>{name}:  {value}</LI>'
        html += '</UL></LI>'
    
    html += '</UL></LI></UL></UL></td></tr></table>'
    return html

def generate_test_section(test_data, index):
    """Generate HTML section for a merged test"""
    test_name = test_data['name']
    status = test_data['status']
    duration = test_data['duration']
    
    html = f'<a name="_{index}"></a><HR COLOR="#6699CC" SIZE="2">'
    html += f'<big><big><b>{test_name}</b></big></big>'
    html += f'<UL><big><b>Status:  </b></big><big><b>{status}</b></big></UL>'
    
    # Combine dataset information from all tests with the same name
    all_datasets = []
    for test_elem in test_data['tests']:
        datasets = get_dataset_info(test_elem)
        all_datasets.extend(datasets)
    
    # If we have datasets, combine them into a single table
    if all_datasets:
        # Use headers from the first dataset (assuming all datasets have the same structure)
        if all_datasets[0]['input_headers'] or all_datasets[0]['output_headers']:
            all_headers = all_datasets[0]['input_headers'] + all_datasets[0]['output_headers'] + ['Time (s)']
            
            html += '<UL><table border="1"><tr>'
            
            # Generate header row
            for i, header in enumerate(all_headers):
                # Set background colors
                if i < len(all_datasets[0]['input_headers']):
                    bg_color = '#FFFFCC'  # Yellow for inputs
                elif i < len(all_datasets[0]['input_headers']) + len(all_datasets[0]['output_headers']):
                    bg_color = '#6699CC'  # Blue for outputs
                else:
                    bg_color = '#EEEEE0'  # Gray for time
                
                html += f'<td bgcolor="{bg_color}" align="center"><b>{header}</b></td>'
            
            html += '</tr>'
            
            # Generate data rows from all datasets
            for dataset in all_datasets:
                # Generate data rows
                max_rows = max(len(dataset['input_values']), len(dataset['output_values']), 1)
                
                for row_idx in range(max_rows):
                    html += '<tr>'
                    
                    # Add input values
                    if row_idx < len(dataset['input_values']):
                        input_row = dataset['input_values'][row_idx]
                        for value in input_row:
                            html += f'<td align="center">{value}</td>'
                        # Pad with empty cells if needed
                        while len(input_row) < len(dataset['input_headers']):
                            html += '<td align="center"></td>'
                    else:
                        # Fill with empty cells
                        for _ in range(len(dataset['input_headers'])):
                            html += '<td align="center"></td>'
                    
                    # Add output values
                    if row_idx < len(dataset['output_values']):
                        output_row = dataset['output_values'][row_idx]
                        for value in output_row:
                            html += f'<td align="center">{value}</td>'
                        # Pad with empty cells if needed
                        while len(output_row) < len(dataset['output_headers']):
                            html += '<td align="center"></td>'
                    else:
                        # Fill with empty cells
                        for _ in range(len(dataset['output_headers'])):
                            html += '<td align="center"></td>'
                    
                    # Add time value
                    if row_idx < len(dataset['times']):
                        _, dur = dataset['times'][row_idx]
                        if dur:
                            # Convert duration from milliseconds to seconds
                            try:
                                time_sec = int(dur) / 1000.0
                                html += f'<td align="center">{time_sec:.2f}</td>'
                            except ValueError:
                                html += '<td align="center">-</td>'
                        else:
                            html += '<td align="center">-</td>'
                    else:
                        html += '<td align="center">-</td>'
                    
                    html += '</tr>'
            
            html += '</table></UL>'
    
    html += f'<br>Duration: {duration} (s)<br><br>'
    html += f'<a href="#TOC">Back to top</a>'
    
    return html

def merge_tests(tests):
    """Merge tests with the same name or I attribute"""
    merged_tests = {}
    
    for test in tests:
        # Get test identifier (I attribute or Name)
        test_id = test.get('I')
        if not test_id:
            test_id = get_test_name(test)
        
        # Get test name
        test_name = get_test_name(test)
        
        # If this is the first test with this ID, initialize it
        if test_id not in merged_tests:
            merged_tests[test_id] = {
                'name': test_name,
                'tests': [test],
                'status': get_test_status(test),
                'duration': float(get_test_duration(test))
            }
        else:
            # Add this test to the existing entry
            merged_tests[test_id]['tests'].append(test)
            # Update duration (add to existing)
            merged_tests[test_id]['duration'] += float(get_test_duration(test))
            # Update status if any test failed
            current_status = get_test_status(test)
            if 'FAIL' in current_status:
                merged_tests[test_id]['status'] = current_status
    
    # Format durations back to string
    for test_data in merged_tests.values():
        test_data['duration'] = f"{test_data['duration']:.2f}"
    
    return merged_tests

def convert_xml_to_html(xml_file, html_file):
    """Main function to convert XML to HTML"""
    # Parse XML file
    tree = ET.parse(xml_file)
    root = tree.getroot()
    
    # Find TestCollection
    test_collection = root.find('.//TestCollection')
    if test_collection is None:
        raise ValueError("TestCollection element not found in XML")
    
    # Get collection name
    collection_name_elem = test_collection.find('Name')
    collection_name = collection_name_elem.text if collection_name_elem is not None else "Unknown Collection"
    
    # Get date information
    date_info = get_date_info(test_collection)
    
    # Get all tests
    tests = test_collection.findall('Test')
    
    # Merge tests with the same name or I attribute
    merged_tests = merge_tests(tests)
    
    # Generate HTML
    html_content = generate_html_header(collection_name, date_info)
    html_content += generate_toc(merged_tests)
    html_content += generate_collection_info(test_collection)
    
    # Generate test sections
    for i, (test_key, test_data) in enumerate(merged_tests.items(), 1):
        html_content += generate_test_section(test_data, i)
    
    # Add final HR
    html_content += '<HR COLOR="#6699CC" SIZE="2">\n'
    html_content += '</body>\n</html>'
    
    # Write HTML file
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(html_content)

if __name__ == "__main__":
    
    input_xml = r"D:\\PythonProject\\pro_PathFinder\\debug\\test8\\report-short.xml"
    output_html = r"D:\\PythonProject\\pro_PathFinder\\debug\\test8\\converted_report_short.html"
    
    try:
        convert_xml_to_html(input_xml, output_html)
        print(f"Successfully converted {input_xml} to {output_html}")
    except Exception as e:
        print(f"Error converting XML to HTML: {str(e)}")