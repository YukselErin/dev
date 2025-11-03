
import unittest
import os
import chroma_handler

class TestChromaHandler(unittest.TestCase):

    def test_add_and_query_robot(self):
        # Create a dummy robot file
        with open("test_robot.robot", "w") as f:
            f.write("<robot name='test_robot'></robot>")

        # Add the robot to the database
        result = chroma_handler.add_robot_to_db("test_robot.robot")
        self.assertEqual(result, "Robot test_robot.robot added to the database.")

        # Query the database for the robot
        results = chroma_handler.query_robots("test_robot")
        self.assertIsNotNone(results)
        self.assertGreater(len(results), 0)

        # Clean up the dummy robot file
        os.remove("test_robot.robot")

if __name__ == '__main__':
    unittest.main()
