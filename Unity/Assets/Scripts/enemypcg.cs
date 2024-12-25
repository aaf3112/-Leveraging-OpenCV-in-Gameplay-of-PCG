using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class enemypcg : MonoBehaviour
{
    public GameObject items;
    public int numberOfInstances = 10;
    public float spacing = 10f; // You can still use spacing if needed for adjustments

    void Start()
    {
        Vector3 position = transform.position; // Starting position

        for (int i = 0; i < numberOfInstances; i++)
        {
            float randomX = Random.Range(10f, 250f); // Random X position between 0 and 300
            float randomY = Random.Range(2f, 8f);  // Generate a random Y value

            position.x = randomX; // Set the X position to the random value
            position.y = randomY;

            Instantiate(items, position, Quaternion.identity);
        }
    }
}
