using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.SceneManagement;

public class MainMenu : MonoBehaviour
{
    public void PlayGame()  
    {
        // Load the main game scene. Replace "GameScene" with your actual game scene name.
        SceneManager.LoadScene("1-1");
    }

    // public void OpenOptions()
    // {
    //     // Load the Options menu or display an options panel
    //     Debug.Log("Opening Options Menu...");
    //     // You can add code here to show a new UI panel for options
    // }

    public void QuitGame()
    {
        Debug.Log("Quitting game...");

        #if UNITY_EDITOR
        UnityEditor.EditorApplication.isPlaying = false;
        #else
        Application.Quit();
        #endif
    }
}