import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
from typing import List, Tuple, Optional
from src.drone import Drone, Waypoint
from matplotlib.animation import FuncAnimation
import os
from datetime import datetime
from .utils import get_logger

class DroneVisualizer:
    def __init__(self, figsize=(12, 8)):
        """
        Initialize the visualization system
        
        Args:
            figsize: Tuple specifying figure size
        """
        self.figsize = figsize
        plt.style.use('seaborn-v0_8')
        self.logger = get_logger(__name__)
        self.logger.info("Initialized DroneVisualizer")

    def plot_3d_trajectory(self, drone: Drone, ax: Optional[Axes3D] = None, 
                         color: str = 'blue', label: Optional[str] = None, 
                         show: bool = True, 
                         trajectory_style: str = 'solid',
                         marker_style: str = 'o'):
        """
        Plot a single drone's 3D trajectory
        
        Args:
            drone: Drone object to plot
            ax: Optional matplotlib axes object
            color: Color of the trajectory
            label: Label for the drone
            show: Whether to display the plot immediately
            trajectory_style: Style of the trajectory line
            marker_style: Style of the waypoint markers
        """
        self.logger.info(f"Plotting trajectory for drone {drone.id}")
        
        if ax is None:
            fig = plt.figure(figsize=self.figsize)
            ax = fig.add_subplot(111, projection='3d')

        x, y, z = zip(*drone.get_trajectory())
        ax.plot(x, y, z, color=color, linestyle=trajectory_style, 
                marker=marker_style, label=label)
        
        # Set labels
        ax.set_xlabel('X (m)')
        ax.set_ylabel('Y (m)')
        ax.set_zlabel('Z (m)')
        
        # Add start and end markers
        ax.scatter(x[0], y[0], z[0], color=color, s=100, marker='^', 
                   label=f"Start {drone.id}" if label else None)
        ax.scatter(x[-1], y[-1], z[-1], color=color, s=100, marker='v', 
                   label=f"End {drone.id}" if label else None)
        
        if show:
            plt.legend()
            plt.title(f"Drone {drone.id} Trajectory")
            plt.show()

    def plot_multiple_trajectories(self, drones: List[Drone], 
                                conflict_points: List[Tuple[float, float, float]] = None,
                                show: bool = True,
                                output_file: str = None):
        """Plot multiple drone trajectories with conflict points"""
        fig = plt.figure(figsize=self.figsize)
        ax = fig.add_subplot(111, projection='3d')

        # Plot each drone's trajectory with enhanced visualization
        for i, drone in enumerate(drones):
            x, y, z = zip(*drone.get_trajectory())
            if i == 0:  # Primary drone
                ax.plot(x, y, z, color='blue', linestyle='--', marker='*', 
                        label=f'Primary Drone')
                ax.scatter(x[-1], y[-1], z[-1], color='blue', s=100, marker='o')
                ax.text(x[-1], y[-1], z[-1], f'Primary Drone\nAlt: {z[-1]:.1f}m', 
                        color='white', backgroundcolor='blue', fontsize=8)
            else:  # Simulated drones
                color = np.random.rand(3,)
                ax.plot(x, y, z, color=color, linestyle='-', marker='o', 
                        label=f'Simulated Drone {i}')
                ax.scatter(x[-1], y[-1], z[-1], color=color, s=100, marker='o')
                ax.text(x[-1], y[-1], z[-1], f'Simulated Drone {i}\nAlt: {z[-1]:.1f}m', 
                        color='white', backgroundcolor=color, fontsize=8)

        # Plot conflict points if any
        if conflict_points:
            x_conf, y_conf, z_conf = zip(*conflict_points)
            ax.scatter(x_conf, y_conf, z_conf, color='red', s=100, 
                      marker='x', label='Conflict Points')
            for x, y, z in zip(x_conf, y_conf, z_conf):
                ax.text(x, y, z, f'Conflict Point\nAlt: {z:.1f}m', 
                        color='white', backgroundcolor='red', fontsize=8)

        # Set labels and title with more information
        ax.set_xlabel('X (m) - East/West Position')
        ax.set_ylabel('Y (m) - North/South Position')
        ax.set_zlabel('Z (m) - Altitude')
        plt.title('Multiple Drone Trajectories')
        
        # Add legend
        ax.legend(loc='upper left', bbox_to_anchor=(1.05, 1), fontsize='small')
        
        if show:
            plt.show()
        
        if output_file:
            plt.savefig(output_file)
            plt.close()

    def create_animation(self, drones: List[Drone], 
                        conflict_points: List[Tuple[float, float, float]] = None,
                        output_dir: str = 'demo_output',
                        filename: str = 'drone_animation.gif'):
        """Create animated visualization of drone movements"""
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        fig = plt.figure(figsize=self.figsize)
        ax = fig.add_subplot(111, projection='3d')
        
        # Plot initial trajectories
        colors = plt.cm.rainbow(np.linspace(0, 1, len(drones)))
        lines = []
        points = []
        
        for i, drone in enumerate(drones):
            line, = ax.plot([], [], [], color=colors[i], marker='o')
            point, = ax.plot([], [], [], 'o', color=colors[i], markersize=10)
            lines.append(line)
            points.append(point)

        # Plot conflict points if provided
        if conflict_points:
            x_conf, y_conf, z_conf = zip(*conflict_points)
            ax.scatter(x_conf, y_conf, z_conf, color='red', s=100, 
                      marker='x', label='Conflict Points')

        # Set labels and title
        ax.set_xlabel('X (m)')
        ax.set_ylabel('Y (m)')
        ax.set_zlabel('Z (m)')
        plt.title("Dynamic Drone Trajectories")

        # Animation function
        def update(frame):
            ax.view_init(elev=30, azim=frame)
            return lines + points

        # Create animation
        anim = FuncAnimation(fig, update, frames=np.arange(0, 360, 5), 
                           interval=50, blit=True)
        
        # Save animation
        full_path = os.path.join(output_dir, filename)
        anim.save(full_path, writer='pillow')
        plt.close()
        
        self.logger.info(f"Saved animation to {full_path}")
