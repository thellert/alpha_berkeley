"""Launcher Service Utilities

Utility functions for URI generation and command handling.
Migrated from legacy implementation with minimal changes.
"""

import urllib.parse
import tempfile
import os
import html
import re
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Union
from dataclasses import dataclass
from enum import Enum
from pydantic import BaseModel, Field
from .models import ExecutableCommand
from configs.logger import get_logger
logger = get_logger("als_assistant", "launcher")
    

class TraceType(Enum):
    """Available trace types for Data Browser plots."""
    LINE = "LINE"
    AREA = "AREA" 
    STEP = "STEP"
    BARS = "BARS"


class LineStyle(Enum):
    """Available line styles for traces."""
    SOLID = "SOLID"
    DASH = "DASH" 
    DOT = "DOT"
    DASHDOT = "DASHDOT"


class PointType(Enum):
    """Available point types for traces."""
    NONE = "NONE"
    CIRCLE = "CIRCLE"
    SQUARE = "SQUARE"
    DIAMOND = "DIAMOND"
    TRIANGLE = "TRIANGLE"


def sanitize_xml_text(text: str) -> str:
    """Sanitize text for safe inclusion in XML content.
    
    This function:
    1. Removes control characters that can break XML parsing
    2. Replaces common problematic characters with safe alternatives
    3. Applies HTML escaping for XML special characters
    
    Args:
        text: Input text that may contain problematic characters
        
    Returns:
        Sanitized text safe for XML inclusion
    """
    if not text:
        return ""
    
    # Log suspicious input for debugging
    if any(ord(c) < 32 and c not in '\t\n\r' for c in text):
        logger.warning(f"Found control characters in XML text: {repr(text)}")
    
    # Replace common problematic characters FIRST
    text = text.replace('°', 'deg')   # Replace degree symbol (remove space to avoid confusion)
    text = text.replace('μ', 'u')     # Replace micro symbol
    text = text.replace('²', '2')     # Replace superscript 2
    text = text.replace('³', '3')     # Replace superscript 3
    
    # Remove control characters (ASCII 0-31 except tab, newline, carriage return)
    # This includes backspace (\x08) and other problematic characters
    text = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', text)
    
    # Handle common temperature patterns that might have been corrupted
    text = re.sub(r'\b0C\b', 'degC', text)  # Fix common 0C -> degC pattern
    text = re.sub(r'\bdeg\s*C\b', 'degC', text)  # Normalize "deg C" to "degC"
    
    # Apply HTML escaping for XML special characters
    text = html.escape(text)
    
    return text


class PVConfig(BaseModel):
    """Configuration for a single PV trace in the Data Browser."""
    name: str = Field(description="PV name (e.g., SR:DCCT)")
    display_name: Optional[str] = Field(default=None, description="Human-readable display name for the PV")
    color_red: int = Field(default=0, description="Red component of RGB color (0-255)")
    color_green: int = Field(default=100, description="Green component of RGB color (0-255)")
    color_blue: int = Field(default=200, description="Blue component of RGB color (0-255)")
    trace_type: TraceType = Field(default=TraceType.LINE, description="Type of trace (LINE, AREA, STEP, BARS)")
    line_style: LineStyle = Field(default=LineStyle.SOLID, description="Line style (SOLID, DASH, DOT, DASHDOT)")
    line_width: int = Field(default=2, description="Line width in pixels")
    point_type: PointType = Field(default=PointType.NONE, description="Point marker type")
    point_size: int = Field(default=2, description="Point marker size")
    axis: int = Field(default=0, description="Which axis to use (0=left, 1=right, etc.)")
    
    @property
    def color(self) -> tuple[int, int, int]:
        """Get color as RGB tuple."""
        return (self.color_red, self.color_green, self.color_blue)


class TimeRange(BaseModel):
    """Time range specification for the Data Browser."""
    start: Union[str, datetime] = Field(description="Start time - can be datetime, 'now', '-2 hours', etc.")
    end: Union[str, datetime] = Field(description="End time - can be datetime, 'now', etc.")


# Annotation support added for Phoebus Data Browser


class AnnotationConfig(BaseModel):
    """Configuration for a plot annotation."""
    text: str = Field(description="Annotation text content")
    time_position: Union[str, datetime] = Field(description="Time position for annotation")
    value_position: float = Field(description="Value position for annotation")
    offset_x: float = Field(default=20.0, description="X offset from position")
    offset_y: float = Field(default=20.0, description="Y offset from position")
    pv_index: int = Field(default=0, description="Index of PV this annotation refers to")

class PlotConfig(BaseModel):
    """High-level configuration for a Data Browser plot - LLM-friendly API."""
    title: str = Field(description="Title for the plot")
    pvs: List[PVConfig] = Field(description="List of PV configurations to plot")
    time_range: Optional[TimeRange] = Field(default=None, description="Time range for the plot")
    annotations: List[AnnotationConfig] = Field(default_factory=list, description="Plot annotations")
    
    # Plot appearance - separate RGB components for Gemini Flash compatibility
    background_red: int = Field(default=255, description="Background red component (0-255)")
    background_green: int = Field(default=255, description="Background green component (0-255)")
    background_blue: int = Field(default=255, description="Background blue component (0-255)")
    foreground_red: int = Field(default=0, description="Foreground red component (0-255)")
    foreground_green: int = Field(default=0, description="Foreground green component (0-255)")
    foreground_blue: int = Field(default=0, description="Foreground blue component (0-255)")
    show_grid: bool = Field(default=True, description="Whether to show grid lines")
    show_legend: bool = Field(default=True, description="Whether to show legend")
    show_toolbar: bool = Field(default=True, description="Whether to show toolbar")
    
    # Time axis
    scroll: bool = Field(default=True, description="Whether to enable scrolling")
    update_period: float = Field(default=3.0, description="Update period in seconds")
    
    # Axis configuration
    axis_name: str = Field(default="Values", description="Name for the axis")
    auto_scale: bool = Field(default=True, description="Whether to auto-scale the axis")
    axis_min: Optional[float] = Field(default=None, description="Minimum axis value (if not auto-scale)")
    axis_max: Optional[float] = Field(default=None, description="Maximum axis value (if not auto-scale)")
    log_scale: bool = Field(default=False, description="Whether to use logarithmic scale")
    
    @property
    def background_color(self) -> tuple[int, int, int]:
        """Get background color as RGB tuple."""
        return (self.background_red, self.background_green, self.background_blue)
    
    @property
    def foreground_color(self) -> tuple[int, int, int]:
        """Get foreground color as RGB tuple."""
        return (self.foreground_red, self.foreground_green, self.foreground_blue)


def add_time_period_annotations(plot_config: PlotConfig, 
                               start_time: Union[str, datetime], 
                               end_time: Union[str, datetime],
                               label: str) -> None:
    """Add annotations to mark a time period since overlays aren't supported.
    
    This function adds three annotations to visually indicate a time range:
    1. A centered label spanning the period
    2. A start marker
    3. An end marker
    
    Args:
        plot_config: The plot configuration to modify
        start_time: Start of the highlighted period  
        end_time: End of the highlighted period
        label: Label for the highlighted period
    """
    # Calculate middle time for the main label
    if isinstance(start_time, datetime) and isinstance(end_time, datetime):
        middle_time = start_time + (end_time - start_time) / 2
    else:
        # For string times, use the start time and let the user position manually
        middle_time = start_time
    
    # Add the main period label in the center
    plot_config.annotations.append(AnnotationConfig(
        text=f"◄── {label} ──►",
        time_position=middle_time,
        value_position=0,  # Will be positioned relative to data range
        offset_x=0,
        offset_y=-50,  # Above the plot area
        pv_index=0
    ))
    
    # Add start marker
    plot_config.annotations.append(AnnotationConfig(
        text="Start",
        time_position=start_time,
        value_position=0,
        offset_x=15,
        offset_y=-25,
        pv_index=0
    ))
    
    # Add end marker  
    plot_config.annotations.append(AnnotationConfig(
        text="End",
        time_position=end_time,
        value_position=0,
        offset_x=-35,
        offset_y=-25,
        pv_index=0
    ))


def create_plt_from_config(plot_config: PlotConfig) -> str:
    """Generate a PLT file from a PlotConfig and return the file path.
    
    This converts the high-level PlotConfig into the detailed XML format.
    """
    logger.info(f"Creating PLT file for plot: {plot_config.title}")
    
    # Use config system to get proper launcher outputs directory
    # This handles container/host mounting correctly
    from configs.config import get_agent_dir
    
    logger.debug(f"Current working directory: {os.getcwd()}")
    
    # Get launcher outputs directory using config system
    launcher_outputs_dir = get_agent_dir('launcher_outputs_dir')
    logger.info(f"Target directory (from config): {launcher_outputs_dir}")
    
    # Ensure the directory exists and log the result
    try:
        os.makedirs(launcher_outputs_dir, exist_ok=True)
        logger.info(f"Directory created/verified: {launcher_outputs_dir}")
        
        # Verify directory is writable
        if os.access(launcher_outputs_dir, os.W_OK):
            logger.debug("Directory is writable")
        else:
            logger.warning("Directory is not writable!")
            
    except Exception as e:
        logger.error(f"Failed to create directory {launcher_outputs_dir}: {e}")
        raise
    
    # Generate timestamped filename
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    temp_fd, temp_path = tempfile.mkstemp(
        suffix='.plt', 
        prefix=f'{timestamp}_als_assistant_databrowser_',
        dir=launcher_outputs_dir
    )
    
    # Format time range
    if plot_config.time_range:
        if isinstance(plot_config.time_range.start, datetime):
            start_str = plot_config.time_range.start.strftime('%Y-%m-%d %H:%M:%S.000')
        else:
            start_str = str(plot_config.time_range.start)
            
        if isinstance(plot_config.time_range.end, datetime):
            end_str = plot_config.time_range.end.strftime('%Y-%m-%d %H:%M:%S.999')
        else:
            end_str = str(plot_config.time_range.end)
    else:
        # Default to last 24 hours
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=24)
        start_str = start_time.strftime('%Y-%m-%d %H:%M:%S.000')
        end_str = end_time.strftime('%Y-%m-%d %H:%M:%S.999')
    
    # Generate XML
    bg = plot_config.background_color
    fg = plot_config.foreground_color
    
    xml_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<databrowser>
  <title>{sanitize_xml_text(plot_config.title)}</title>
  <show_toolbar>{str(plot_config.show_toolbar).lower()}</show_toolbar>
  <show_legend>{str(plot_config.show_legend).lower()}</show_legend>
  <update_period>{plot_config.update_period}</update_period>
  <scroll_step>5</scroll_step>
  <scroll>{str(plot_config.scroll).lower()}</scroll>
  <start>{sanitize_xml_text(start_str)}</start>
  <end>{sanitize_xml_text(end_str)}</end>
  <archive_rescale>STAGGER</archive_rescale>
  <foreground>
    <red>{fg[0]}</red>
    <green>{fg[1]}</green>
    <blue>{fg[2]}</blue>
  </foreground>
  <background>
    <red>{bg[0]}</red>
    <green>{bg[1]}</green>
    <blue>{bg[2]}</blue>
  </background>
  <title_font>Liberation Sans|16|1</title_font>
  <label_font>Liberation Sans|12|0</label_font>
  <scale_font>Liberation Sans|10|0</scale_font>
  <legend_font>Liberation Sans|12|0</legend_font>
  <axes>
    <axis>
      <visible>true</visible>
      <name>{sanitize_xml_text(plot_config.axis_name)}</name>
      <use_axis_name>true</use_axis_name>
      <use_trace_names>true</use_trace_names>
      <right>false</right>
      <color>
        <red>{fg[0]}</red>
        <green>{fg[1]}</green>
        <blue>{fg[2]}</blue>
      </color>'''
    
    # Add axis limits
    if plot_config.axis_min is not None and plot_config.axis_max is not None:
        xml_content += f'''
      <min>{plot_config.axis_min}</min>
      <max>{plot_config.axis_max}</max>'''
    else:
        xml_content += '''
      <min>0.0</min>
      <max>100.0</max>'''
    
    xml_content += f'''
      <grid>{str(plot_config.show_grid).lower()}</grid>
      <autoscale>{str(plot_config.auto_scale).lower()}</autoscale>
      <log_scale>{str(plot_config.log_scale).lower()}</log_scale>
    </axis>
  </axes>
  <pvlist>'''
    
    # Add each PV
    for pv in plot_config.pvs:
        display_name = pv.display_name or pv.name
        color = pv.color  # Use the property that returns tuple
        
        xml_content += f'''
    <pv>
      <display_name>{sanitize_xml_text(display_name)}</display_name>
      <visible>true</visible>
      <name>{sanitize_xml_text(pv.name)}</name>
      <axis>{pv.axis}</axis>
      <color>
        <red>{color[0]}</red>
        <green>{color[1]}</green>
        <blue>{color[2]}</blue>
      </color>
      <trace_type>{pv.trace_type.value}</trace_type>
      <linewidth>{pv.line_width}</linewidth>
      <line_style>{pv.line_style.value}</line_style>
      <point_type>{pv.point_type.value}</point_type>
      <point_size>{pv.point_size}</point_size>
      <waveform_index>0</waveform_index>
      <period>0.0</period>
      <ring_size>5000</ring_size>
      <request>OPTIMIZED</request>
      <archive>
        <name>archappl</name>
        <url>pbraw://controls-web.als.lbl.gov/archappl_retrieve</url>
        <key>1</key>
      </archive>
    </pv>'''
    
    xml_content += '''
  </pvlist>'''
    
    # Add annotations section if any annotations exist
    if plot_config.annotations:
        xml_content += '''
  <annotations>'''
        
        for annotation in plot_config.annotations:
            # Format time position
            if isinstance(annotation.time_position, datetime):
                time_str = annotation.time_position.strftime('%Y-%m-%d %H:%M:%S.000')
            else:
                time_str = str(annotation.time_position)
            
            xml_content += f'''
    <annotation>
      <pv>{annotation.pv_index}</pv>
      <time>{sanitize_xml_text(time_str)}</time>
      <value>{annotation.value_position}</value>
      <offset>
        <x>{annotation.offset_x}</x>
        <y>{annotation.offset_y}</y>
      </offset>
      <text>{sanitize_xml_text(annotation.text)}</text>
    </annotation>'''
        
        xml_content += '''
  </annotations>'''
    
    xml_content += '''
</databrowser>'''
    
    # Write the file
    logger.debug(f"Writing PLT file to: {temp_path}")
    try:
        with os.fdopen(temp_fd, 'w') as f:
            f.write(xml_content)
        logger.info(f"Successfully created PLT file: {temp_path}")
        
        # Verify file exists and get its size
        if os.path.exists(temp_path):
            file_size = os.path.getsize(temp_path)
            logger.info(f"PLT file verified: {temp_path} (size: {file_size} bytes)")
        else:
            logger.error(f"PLT file does not exist after writing: {temp_path}")
            
    except Exception as e:
        logger.error(f"Failed to write PLT file: {e}")
        raise
    
    return temp_path


def create_launch_uri_from_executable_command(command: ExecutableCommand) -> tuple[str, str]:
    """Converts an ExecutableCommand object into a 'myapp://' URI.
    
    This is the core innovation from the legacy implementation - it creates
    a URI that can be handled by the desktop to execute commands on the user's
    machine while the agent runs in a different network context.
    
    Handles container-to-host path translation for file arguments.
    
    Args:
        command: The command to convert to a URI
        
    Returns:
        Tuple of (command_name, launch_uri)
        
    Note:
        The URI is structured as myapp://launch_tool/<encoded_command_plus_args>.
        Each part of the command is URL-encoded and joined with '%20'.
        This matches the format expected by launch_tool.sh.
    """
    from configs.config import get_agent_dir
    import re
    
    logger.debug(f"Creating launch URI for command: {command['name']}")
    
    # URL-encode executable
    encoded_parts = [urllib.parse.quote(str(command["executable"]), safe='/')]
    
    # Process arguments with container-to-host path translation
    for arg in command["args"]:
        arg_str = str(arg)
        
        # Check if this argument is a container path that needs translation
        if _is_container_agent_data_path(arg_str):
            host_path = _translate_container_path_to_host(arg_str)
            logger.info(f"Translated container path: {arg_str} -> {host_path}")
            encoded_parts.append(urllib.parse.quote(host_path, safe='/'))
        else:
            encoded_parts.append(urllib.parse.quote(arg_str, safe='/'))
    
    # Join the encoded parts with '%20' to represent spaces between them
    encoded_command_string = "%20".join(encoded_parts)
    
    # The launch_tool.sh script expects the command after "myapp://launch_tool/"
    # If command.executable starts with '/', encoded_command_string will start with '/',
    # leading to "myapp://launch_tool//..." which matches the observed working format
    uri = f"myapp://launch_tool/{encoded_command_string}"
    
    logger.debug(f"Generated launch URI: {uri}")
    return command["name"], uri


def _is_container_agent_data_path(path: str) -> bool:
    """Check if a path is a container agent data path that needs translation."""
    container_patterns = [
        r'^/app/_agent_data/',
        r'^/pipelines/_agent_data/',
        r'^/jupyter/_agent_data/'
    ]
    
    for pattern in container_patterns:
        if re.match(pattern, path):
            return True
    return False


def _translate_container_path_to_host(container_path: str) -> str:
    """Translate a container agent data path to the corresponding host path."""
    from configs.config import get_agent_dir
    import re
    
    # Extract the subdirectory and filename from the container path
    # Pattern: /app/_agent_data/subdir/filename -> subdir/filename
    match = re.match(r'^/(?:app|pipelines|jupyter)/_agent_data/([^/]+)/(.*)', container_path)
    
    if match:
        subdir = match.group(1)
        filename = match.group(2)
        
        # Get the host path for this subdirectory
        host_dir = get_agent_dir(f"{subdir}_dir", host_path=True)
        host_path = os.path.join(host_dir, filename)
        
        logger.debug(f"Path translation: {container_path} -> {host_path}")
        return host_path
    else:
        # Fallback: return original path if pattern doesn't match
        logger.warning(f"Could not translate container path: {container_path}")
        return container_path


def create_advanced_databrowser_command(
    executable_path: str,
    plot_config: PlotConfig
) -> ExecutableCommand:
    """Create a Data Browser command using advanced PlotConfig - for LLM use.
    
    This is the function that LLMs should use for complex plot configurations.
    
    Args:
        executable_path: Path to the Phoebus executable
        plot_config: Advanced plot configuration
        
    Returns:
        ExecutableCommand ready for URI generation
    """

    logger.info(f"Creating advanced databrowser command for executable: {executable_path}")
    plt_file = create_plt_from_config(plot_config)
    logger.info(f"PLT file created at: {plt_file}")
    pv_names = [pv.name for pv in plot_config.pvs]
    
    return ExecutableCommand({
        "name": f"Launch Data Browser: {plot_config.title}",
        "executable": executable_path,
        "args": ["-resource", plt_file],
        "description": f"Launches advanced Data Browser plot '{plot_config.title}' with {len(pv_names)} PVs: {', '.join(pv_names[:3])}{'...' if len(pv_names) > 3 else ''}"
    })
