import chroma_handler
import os

# Add a dummy robot to the database
with open("dummy_robot.robot", "w") as f:
    f.write("<robot name='dummy_robot'></robot>")
chroma_handler.add_robot_to_db("dummy_robot.robot")

# Query the database for the robot
retrieved_robots = chroma_handler.query_robots("dummy_robot")

# Print the retrieved robots
print(retrieved_robots)

# Clean up the dummy robot file
os.remove("dummy_robot.robot")