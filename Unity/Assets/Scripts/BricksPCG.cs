using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class BricksPCG : MonoBehaviour
{
    public GameObject brick;
    public int numberOfInstances = 40;
    public float spacing = 20f; // Adjust the spacing between instances

    void Start()
    {
        Vector3 position = transform.position; // Starting position

        for (int i = 0; i < numberOfInstances; i++)
        {
            float randomY = Random.Range(2f, 4f); // Generate a random Y value
            
            Instantiate(brick, position, Quaternion.identity);
            position.x += spacing;
            position.y = randomY;
        }
    }
}