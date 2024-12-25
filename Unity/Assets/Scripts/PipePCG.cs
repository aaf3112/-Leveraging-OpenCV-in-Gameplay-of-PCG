using UnityEngine;

public class PipePCG : MonoBehaviour
{
    public GameObject pipePrefab; // Assign your pipe prefab here
    public int minPipes = 3;      // Minimum number of pipes to spawn
    public int maxPipes = 6;      // Maximum number of pipes to spawn
    public float minX = 30f;      // Minimum x position
    public float maxX = 200f;     // Maximum x position
    public float minY = 1.5f;       // Minimum y position
    public float maxY = 3f;       // Maximum y position
    public float minSpacing = 30f; // Minimum spacing between pipes
    public float maxSpacing = 90f; // Maximum spacing between pipes

    void Start()
    {
        // Determine the number of pipes to spawn
        int numberOfPipes = Random.Range(minPipes, maxPipes + 1);

        // Start the X position at minX
        float currentX = minX;

        for (int i = 0; i < numberOfPipes; i++)
        {
            // Generate a random Y position within the specified range
            float randomY = Random.Range(minY, maxY);

            // Create a new position for the pipe
            Vector3 spawnPosition = new Vector3(currentX, randomY, 0f);

            // Instantiate the pipe at the calculated position
            Instantiate(pipePrefab, spawnPosition, Quaternion.identity);

            // Randomize the spacing for the next pipe
            float randomSpacing = Random.Range(minSpacing, maxSpacing);

            // Update currentX for the next pipe, ensuring it stays within maxX
            currentX += randomSpacing;

            if (currentX > maxX) break; // Prevent spawning beyond maxX
        }
    }
}
