# src/applications/bolt/ply_quality_analyzer.py
"""
PLY Quality Analyzer for BOLT Beamline System.

This module provides comprehensive quality assessment for 3D reconstructions
from photogrammetry scans using trimesh and advanced geometric analysis.
"""

import numpy as np
import trimesh
from pathlib import Path
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple, Any
import warnings

warnings.filterwarnings('ignore')

@dataclass
class QualityMetrics:
    """Comprehensive quality metrics for 3D reconstructions."""
    
    # Basic mesh properties
    vertex_count: int = 0
    face_count: int = 0
    is_watertight: bool = False
    is_winding_consistent: bool = False
    
    # Geometric quality metrics
    surface_area: float = 0.0
    volume: float = 0.0
    bounding_box_volume: float = 0.0
    
    # Mesh quality indicators
    aspect_ratio_stats: Dict[str, float] = None
    edge_length_stats: Dict[str, float] = None
    
    # Reconstruction-specific metrics
    hole_count: int = 0
    noise_level: float = 0.0
    completeness_score: float = 0.0
    
    # Overall quality score
    overall_quality_score: float = 0.0
    
    # Defect detection
    detected_defects: List[str] = None
    critical_issues: List[str] = None

class PLYQualityAnalyzer:
    """Advanced quality analyzer for PLY files from photogrammetry reconstructions."""
    
    def __init__(self):
        self.quality_thresholds = {
            'excellent': 0.9,
            'good': 0.75,
            'fair': 0.6,
            'poor': 0.4
        }
        
    def analyze_ply_file(self, ply_path: str) -> Tuple[QualityMetrics, List[Dict]]:
        """
        Comprehensive analysis of PLY file quality.
        
        Args:
            ply_path: Path to the PLY file
            
        Returns:
            Tuple of quality metrics and improvement recommendations
        """
        
        if not Path(ply_path).exists():
            raise FileNotFoundError(f"PLY file not found: {ply_path}")
            
        # Load mesh with trimesh
        mesh = self._load_with_trimesh(ply_path)
        
        # Calculate comprehensive metrics
        metrics = self._calculate_quality_metrics(mesh)
        
        # Generate improvement recommendations
        recommendations = self._generate_recommendations(metrics, mesh)
        
        return metrics, recommendations
    
    def _load_with_trimesh(self, ply_path: str) -> trimesh.Trimesh:
        """Load PLY file using trimesh."""
        try:
            mesh = trimesh.load(ply_path)
            if not isinstance(mesh, trimesh.Trimesh):
                # Handle point clouds or scenes
                if hasattr(mesh, 'geometry'):
                    geometries = list(mesh.geometry.values())
                    if geometries:
                        mesh = geometries[0]
                else:
                    raise ValueError("No valid mesh geometry found")
            return mesh
        except Exception as e:
            print(f"Warning: Failed to load with trimesh: {e}")
            return None
    
    def _calculate_quality_metrics(self, mesh: trimesh.Trimesh) -> QualityMetrics:
        """Calculate comprehensive quality metrics."""
        
        metrics = QualityMetrics()
        
        if mesh is None:
            return metrics
        
        # Basic mesh properties
        metrics.vertex_count = len(mesh.vertices)
        metrics.face_count = len(mesh.faces)
        metrics.is_watertight = mesh.is_watertight
        metrics.is_winding_consistent = mesh.is_winding_consistent
        
        # Geometric properties
        try:
            metrics.surface_area = mesh.area
            if mesh.is_watertight:
                metrics.volume = abs(mesh.volume)
            metrics.bounding_box_volume = mesh.bounding_box.volume
            
        except Exception as e:
            print(f"Warning: Error calculating geometric properties: {e}")
        
        # Mesh quality analysis
        metrics = self._analyze_mesh_quality(mesh, metrics)
        
        # Calculate overall quality scores
        metrics = self._calculate_quality_scores(metrics)
        
        return metrics
    
    def _analyze_mesh_quality(self, mesh: trimesh.Trimesh, 
                            metrics: QualityMetrics) -> QualityMetrics:
        """Analyze mesh quality using trimesh."""
        
        try:
            # Triangle aspect ratio analysis
            if len(mesh.faces) > 0:
                face_angles = mesh.face_angles
                aspect_ratios = []
                
                for face_angle_set in face_angles:
                    if len(face_angle_set) == 3:
                        max_angle = np.max(face_angle_set)
                        min_angle = np.min(face_angle_set)
                        aspect_ratio = max_angle / max(min_angle, 0.01)
                        aspect_ratios.append(aspect_ratio)
                
                if aspect_ratios:
                    metrics.aspect_ratio_stats = {
                        'mean': float(np.mean(aspect_ratios)),
                        'std': float(np.std(aspect_ratios)),
                        'min': float(np.min(aspect_ratios)),
                        'max': float(np.max(aspect_ratios))
                    }
            
            # Edge length analysis
            if len(mesh.edges) > 0:
                edge_lengths = mesh.edges_unique_length
                if len(edge_lengths) > 0:
                    metrics.edge_length_stats = {
                        'mean': float(np.mean(edge_lengths)),
                        'std': float(np.std(edge_lengths)),
                        'min': float(np.min(edge_lengths)),
                        'max': float(np.max(edge_lengths))
                    }
            
            # Hole detection
            if not mesh.is_watertight:
                # Count boundary edges to estimate holes
                boundary_edges = mesh.edges[mesh.edges_unique_inverse]
                metrics.hole_count = len(boundary_edges) // 2  # Rough estimate
            
            # Noise level estimation using surface curvature
            if len(mesh.vertices) > 100:
                try:
                    vertex_normals = mesh.vertex_normals
                    curvatures = []
                    
                    for i, vertex in enumerate(mesh.vertices):
                        neighbors = list(mesh.vertex_adjacency_graph.neighbors(i))
                        if len(neighbors) > 2:
                            neighbor_normals = vertex_normals[neighbors]
                            normal_variations = np.linalg.norm(
                                neighbor_normals - vertex_normals[i], axis=1
                            )
                            curvatures.append(np.mean(normal_variations))
                    
                    if curvatures:
                        metrics.noise_level = float(np.std(curvatures))
                
                except Exception as e:
                    print(f"Warning: Error calculating noise level: {e}")
                    metrics.noise_level = 0.0
            
        except Exception as e:
            print(f"Warning: Error in mesh quality analysis: {e}")
        
        return metrics
    
    def _calculate_quality_scores(self, metrics: QualityMetrics) -> QualityMetrics:
        """Calculate overall quality scores."""
        
        scores = []
        
        # Mesh topology score
        topology_score = 1.0
        if not metrics.is_watertight:
            topology_score *= 0.7
        if not metrics.is_winding_consistent:
            topology_score *= 0.8
        if metrics.hole_count > 0:
            topology_score *= max(0.3, 1.0 - metrics.hole_count * 0.1)
        
        scores.append(topology_score)
        
        # Geometric accuracy score
        geometric_score = 1.0
        
        # Penalize high noise
        if metrics.noise_level > 0:
            geometric_score *= max(0.2, 1.0 - metrics.noise_level)
        
        # Penalize poor aspect ratios
        if metrics.aspect_ratio_stats:
            mean_aspect_ratio = metrics.aspect_ratio_stats.get('mean', 1.0)
            if mean_aspect_ratio > 3.0:  # Poor triangles
                geometric_score *= max(0.3, 1.0 - (mean_aspect_ratio - 3.0) * 0.1)
        
        scores.append(geometric_score)
        
        # Overall quality score
        metrics.overall_quality_score = np.mean(scores)
        
        # Detect critical issues
        metrics.critical_issues = []
        metrics.detected_defects = []
        
        if not metrics.is_watertight:
            metrics.detected_defects.append("Non-watertight mesh")
        if metrics.hole_count > 5:
            metrics.critical_issues.append("Excessive holes in reconstruction")
        if metrics.noise_level > 0.5:
            metrics.critical_issues.append("High noise level")
        if metrics.vertex_count < 1000:
            metrics.detected_defects.append("Low vertex density")
        if metrics.overall_quality_score < 0.4:
            metrics.critical_issues.append("Poor overall quality")
        
        return metrics
    
    def _generate_recommendations(self, metrics: QualityMetrics, 
                                mesh: trimesh.Trimesh) -> List[Dict]:
        """Generate specific improvement recommendations."""
        
        recommendations = []
        
        # Critical quality issues
        if metrics.overall_quality_score < self.quality_thresholds['poor']:
            recommendations.append({
                'category': 'scan_parameters',
                'priority': 'critical',
                'issue': 'Very poor reconstruction quality',
                'recommendation': 'Increase number of projections and reduce angular step size',
                'specific_parameters': {
                    'num_projections': 'increase by 50-100%',
                    'angular_step': 'reduce to 1-2 degrees',
                    'exposure_time': 'increase by 20-30%'
                }
            })
        
        # Hole detection recommendations
        if metrics.hole_count > 3:
            recommendations.append({
                'category': 'scan_parameters',
                'priority': 'high',
                'issue': f'Multiple holes detected ({metrics.hole_count})',
                'recommendation': 'Increase angular coverage and projection density',
                'specific_parameters': {
                    'start_angle': 0,
                    'end_angle': 360,
                    'num_projections': max(180, metrics.hole_count * 30),
                    'overlap_ratio': 0.8
                }
            })
        
        # Non-watertight mesh
        if not metrics.is_watertight:
            recommendations.append({
                'category': 'reconstruction_settings',
                'priority': 'high',
                'issue': 'Non-watertight mesh reconstruction',
                'recommendation': 'Adjust reconstruction algorithm parameters',
                'specific_parameters': {
                    'surface_reconstruction': 'Poisson with higher depth',
                    'hole_filling': 'enable',
                    'smoothing_iterations': 3
                }
            })
        
        return recommendations
    
    def get_quality_summary(self, metrics: QualityMetrics) -> str:
        """Generate a human-readable quality summary."""
        
        quality_level = 'poor'
        for level, threshold in self.quality_thresholds.items():
            if metrics.overall_quality_score >= threshold:
                quality_level = level
                break
        
        summary = f"""
=== 3D Reconstruction Quality Analysis ===

Overall Quality: {quality_level.upper()} ({metrics.overall_quality_score:.2f}/1.00)

Mesh Properties:
- Vertices: {metrics.vertex_count:,}
- Faces: {metrics.face_count:,}
- Watertight: {'Yes' if metrics.is_watertight else 'No'}
- Holes detected: {metrics.hole_count}

Quality Scores:
- Overall Quality: {metrics.overall_quality_score:.2f}/1.00
- Noise Level: {metrics.noise_level:.3f}

"""
        
        if metrics.critical_issues:
            summary += "Critical Issues:\n"
            for issue in metrics.critical_issues:
                summary += f"⚠️  {issue}\n"
            summary += "\n"
        
        if metrics.detected_defects:
            summary += "Detected Defects:\n"
            for defect in metrics.detected_defects:
                summary += f"🔍 {defect}\n"
        
        return summary