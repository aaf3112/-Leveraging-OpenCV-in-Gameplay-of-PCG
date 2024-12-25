using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.SceneManagement;

public class PauseMenu : MonoBehaviour {

    public static bool GameIsPaused = false;
    public GameObject pauseMenuUI;

    // Update is called once per frame
    void Update() {
        if (Input.GetKeyDown(KeyCode.Escape)) {
            if(GameIsPaused) {
                Resume();
            } else {
                Pause();
            }
        }
    }

public void Resume()
{
    if (pauseMenuUI != null)  // Check if pauseMenuUI is not null
    {
        pauseMenuUI.SetActive(false);
    }
    Time.timeScale = 1f;
    GameIsPaused = false;
}

void Pause()
{
    if (pauseMenuUI != null)  // Check if pauseMenuUI is not null
    {
        pauseMenuUI.SetActive(true);
    }
    Time.timeScale = 0f;
    GameIsPaused = true;
}


    public void LoadMenu()
    {
        SceneManager.LoadScene("Menu");
        Time.timeScale = 1f;
    }

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