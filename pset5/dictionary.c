/**
 * dictionary.c
 *
 * Computer Science 50
 * Problem Set 5
 *
 * Implements a dictionary's functionality.
 */

#include <stdbool.h>
#include <stdio.h>
#include "dictionary.h"
#include <stdlib.h>
#include <ctype.h>


 // struct which creates a Trie
struct Node
    {
        struct Node* next[27];
        bool flag;
    };

// head of Trie
struct Node* head;
/**
 * Returns true if word is in dictionary else false.
 */
bool check(const char* word)
{
    int test1;
    bool checked = false;
    struct Node* Traverse = head;
    if (Traverse == NULL)
    {
        printf("problem with Traverse pointer in check function. \n");
        return 1;    
    }
    
    for(int i = 0; i < 46; i++ )
    {
        test1 = tolower(word[i]);
        if(test1 == '\'')
            test1 = 26;
        else
            test1 -= 97;
        
        if((*Traverse).next[test1] == NULL)
        {
            break;
        }
        else
        {
            Traverse = (*Traverse).next[test1];
        }
        if(word[i+1] == '\0')
        {
            if((*Traverse).flag == true)
                checked = true;
            break;
        }
    }
    return checked;
}


// initializing counter to check how many words loaded from dictionary
int counter = 0;
/**
 * Loads dictionary into memory.  Returns true if successful else false.
 */


bool load(const char* dictionary)
{
    // open dictionary
    FILE* dict = fopen(dictionary, "r");
    if (dict == NULL)
        return false;
   
   
    // allocating memory for Trie's head
    head = malloc(sizeof(struct Node));
        if (head == NULL)
            return false;
      
    // temporary array for new word
    char temp[47];
    
    // loading new word into temp
    while(fgets(temp, 47, dict) != NULL)
    {
        counter++;
        // temporary pointer to head of the trie
        struct Node* TEMP = head;
        
        // iterating thru new word
        for(int k=0; k<46; k++ )
        {   
            // determining the place in the array(trie) for each character (must be lowercase)
            int i;
            // check if it's the end of the word, if yes, set bool to true and break from the loop
            if(temp[k] == '\n' )
            {
                (*TEMP).flag = true;
                break;
            }
            else if(temp[k] == '\'')
                i = 26;
            
            else
                i = temp[k] - 97;
            
            // adding new node/array to trie if not existing
            if((*TEMP).next[i] == NULL)
            {
                (*TEMP).next[i] = malloc(sizeof(struct Node));
                if((*TEMP).next[i] == NULL)
                    return false;
                TEMP = (*TEMP).next[i];
            }
            
            // following the pointer to next node if existing.
            else
            {
                TEMP = (*TEMP).next[i];
            }
            
            
        }
    }
    fclose(dict);
    return true;
}

/**
 * Returns number of words in dictionary if loaded else 0 if not yet loaded.
 */
unsigned int size(void)
{
        return counter;
}

/**
 * Unloads dictionary from memory.  Returns true if successful else false.
 */
bool Delete (struct Node* node)
{
    if(node == NULL)
        return false;
        
    for (int d = 0; d<27; d++)
    {
        if(node->next[d] != NULL)
            Delete(node->next[d]);
    }
    
    free(node);
    return true;
}
bool unload(void)
{
    if (Delete(head) == true)
       return true;
    else
        return false;
}
