# Software License Agreement (BSD License)
#
# Copyright (c) 2012-2014, Southwest Research Institute
# Copyright (c) 2014-2015, TU Delft Robotics Institute
# Copyright (c) 2020, Norwegian University of Science and Technology
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#  * Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
#  * Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
#  * Neither the name of the Southwest Research Institute, nor the names
#    of its contributors may be used to endorse or promote products derived
#    from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

from typing import List
import copy
import threading
import queue
import logging
import time

Vector = List[float]


class JointTrajectoryPoint:
    def __init__(self):
        self.positions: Vector = []
        self.velocities: Vector = []
        self.accelerations: Vector = []
        self.effort: Vector = []
        self.time_from_start: float = 0.0


class MotionControllerSimulator:
    def __init__(
        self,
        num_joints: int,
        initial_joint_state: Vector,
        update_rate: int = 100,
        buffer_size: int = 0,
    ):
        # Class lock
        self.lock: threading.Lock = threading.Lock()

        # Motion loop update rate (higher update rates result in smoother simulated motion)
        self.update_rate: int = update_rate
        logging.debug("Setting motion update rate (hz): %f", self.update_rate)

        # Initialize joint position
        self.joint_positions: Vector = initial_joint_state
        logging.debug("Setting initial joint state: %s", str(initial_joint_state))

        # Initialize motion buffer (contains joint position lists)
        self.motion_buffer = queue.Queue(buffer_size)
        logging.debug("Setting motion buffer size: %i", buffer_size)

        # Shutdown signal
        self.sig_shutdown: bool = False

        # Stop signal
        self.sig_stop: bool = False

        # Motion thread
        self.motion_thread: threading.Thread = threading.Thread(
            target=self._motion_worker
        )
        self.motion_thread.daemon = True
        self.motion_thread.start()

    def add_motion_waypoint(self, point: JointTrajectoryPoint):
        self.motion_buffer.put(point)

    def get_joint_positions(self) -> Vector:
        with self.lock:
            return self.joint_positions[:]

    def is_in_motion(self) -> bool:
        return not self.motion_buffer.empty()

    def shutdown(self):
        self.sig_shutdown = True
        logging.debug("Motion_Controller shutdown signaled")

    def stop(self):
        logging.debug("Motion_Controller stop signaled")
        with self.lock:
            self._clear_buffer()
            self.sig_stop = True

    def interpolate(
        self,
        last_pt: JointTrajectoryPoint,
        current_pt: JointTrajectoryPoint,
        alpha: float,
    ):
        intermediate_pt = JointTrajectoryPoint()
        for last_joint, current_joint in zip(last_pt.positions, current_pt.positions):
            intermediate_pt.positions.append(
                last_joint + alpha * (current_joint - last_joint)
            )
        intermediate_pt.time_from_start = last_pt.time_from_start + alpha * (
            current_pt.time_from_start - last_pt.time_from_start
        )
        return intermediate_pt

    def accelerate(
        self,
        last_pt: JointTrajectoryPoint,
        current_pt: JointTrajectoryPoint,
        current_time: float,
        delta_time: float,
    ):
        intermediate_pt = JointTrajectoryPoint()
        for last_joint, current_joint, last_vel, current_vel in zip(
            last_pt.positions,
            current_pt.positions,
            last_pt.velocities,
            current_pt.velocities,
        ):
            delta_x = current_joint - last_joint
            dv = current_vel + last_vel
            a1 = 6 * delta_x / pow(delta_time, 2) - 2 * (dv + last_vel) / delta_time
            a2 = -12 * delta_x / pow(delta_time, 3) + 6 * dv / pow(delta_time, 2)
            current_pos = (
                last_joint
                + last_vel * current_time
                + a1 * pow(current_time, 2) / 2
                + a2 * pow(current_time, 3) / 6
            )
            intermediate_pt.positions.append(current_pos)
        intermediate_pt.time_from_start = last_pt.time_from_start + current_time

        return intermediate_pt

    def _clear_buffer(self):
        with self.motion_buffer.mutex:
            self.motion_buffer.queue.clear()

    def _move_to(self, point, dur: float):
        time.sleep(dur)

        with self.lock:
            if not self.sig_stop:
                self.joint_positions = point.positions[:]
            else:
                logging.debug("Stopping motion immediately, clearing stop signal")
                self.sig_stop = False

    def _motion_worker(self):
        logging.debug("Starting motion worker in motion controller simulator")
        if self.update_rate != 0.0:
            update_duration = 1.0 / self.update_rate
        last_goal_point = JointTrajectoryPoint()

        with self.lock:
            last_goal_point.positions = self.joint_positions[:]

        while not self.sig_shutdown:
            try:
                current_goal_point = self.motion_buffer.get()

                # If the current time from start is less than the last, then it's a new trajectory
                if current_goal_point.time_from_start < last_goal_point.time_from_start:
                    move_duration = current_goal_point.time_from_start
                # Else it's an existing trajectory and subtract the two
                else:
                    # If current move duration is greater than update_duration, move arm to interpolated joint position
                    # Provide an exception to this rule: if update rate is <=0, do not add interpolated points
                    move_duration = (
                        current_goal_point.time_from_start
                        - last_goal_point.time_from_start
                    )
                    if self.update_rate > 0:
                        starting_goal_point = copy.deepcopy(last_goal_point)
                        full_duration = move_duration
                        while update_duration < move_duration:
                            if (
                                not starting_goal_point.velocities
                                or not current_goal_point.velocities
                            ):
                                intermediate_goal_point = self.interpolate(
                                    last_goal_point,
                                    current_goal_point,
                                    update_duration / move_duration,
                                )
                            else:
                                intermediate_goal_point = self.accelerate(
                                    starting_goal_point,
                                    current_goal_point,
                                    full_duration - move_duration + update_duration,
                                    full_duration,
                                )
                            self._move_to(
                                intermediate_goal_point, update_duration
                            )  # TODO should this use min(update_duration, 0.5*move_duration) to smooth timing?
                            last_goal_point = copy.deepcopy(intermediate_goal_point)
                            move_duration = (
                                current_goal_point.time_from_start
                                - intermediate_goal_point.time_from_start
                            )

                self._move_to(current_goal_point, move_duration)
                last_goal_point = copy.deepcopy(current_goal_point)

            except Exception as e:
                logging.error("Unexpected exception: %s", e)

        logging.debug("Shutting down motion controller")