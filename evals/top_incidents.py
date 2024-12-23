import asyncio
import os
import time
import logging

import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from collections import Counter
from sklearn.metrics.pairwise import cosine_similarity
import re
import csv
from dotenv import load_dotenv

## Analyze IT Helpdesk Incidents.
## Print top 30 Incident types by frequency.
## Prepare training data for IT Helpdesk Incidents - Incident Type, Short Description and Work Notes.

def preprocess_description(text):
    # Normalize common patterns
    text = text.lower()
    # Remove punctuation
    text = re.sub(r'[^\w\s]', '', text)
    # Standardize common variations
    text = re.sub(r'(want|need|needs|requesting|request)\s+to?\s*', '', text)
    text = re.sub(r'(unlock|unlocked)', 'unlock', text)
    text = re.sub(r'(account|acct)', 'account', text)
    text = re.sub(r'pw', 'password', text)
    # Remove case numbers, dates, names, and specific details
    text = re.sub(r'cb\s*-\s*\d+', '', text)
    text = re.sub(r'\d+/\d+/\d+', '', text)
    text = re.sub(r'\d+(?:st|nd|rd|th)', '', text)
    text = re.sub(r'\d+', '', text)
    # Remove specific locations
    text = re.sub(r'floor.*|office.*', '', text)
    # Remove specific names (assuming they're in Title Case)
    text = re.sub(r'[A-Z][a-z]+\s+[A-Z][a-z]+', '', text)
    return text.strip()

def preprocess_notes(text):
    # Normalize work notes specific patterns
    if pd.isna(text) or str(text).strip() == '':
            return ""
    text = text.lower()
    # Remove Work Notes header
    parts = text.split("(work notes)\n", 2)
    text = parts[2] if len(parts) > 2 else text
    # Replace newlines with periods
    text = text.replace('\n\n', '.')
    text = text.replace('\n', '.')
    text = text.replace(' .', '.')
    # Replace multiple periods with a single period
    text = re.sub(r'\.+', '. ', text)
    text = text.replace('..', '.')
    # Remove timestamps and dates
    text = re.sub(r'\d{1,2}:\d{2}(:\d{2})?(\s*[ap]m)?', '', text)
    text = re.sub(r'\d{1,2}/\d{1,2}/\d{2,4}', '', text)
    # Remove email addresses
    text = re.sub(r'\S+@\S+\.\S+', '', text)
    # Remove ticket/case numbers
    text = re.sub(r'(ticket|case|ref)\s*#?\s*\d+', '', text)
    # Remove common technical terms variations
    text = re.sub(r'(password|pwd|pw)\s*(reset|change)', 'password reset', text)
    text = re.sub(r'(unlocked|unlock|unblock)', 'unlock', text)
    text = re.sub(r'(account|acct)', 'account', text)
    # Remove common action verbs variations
    text = re.sub(r'(performed|completed|done|finished|executed)', 'complete', text)
    text = re.sub(r'(verified|checked|confirmed|validated)', 'verify', text)
    # Remove special characters but keep important technical symbols
    text = re.sub(r'[^\w\s\-_/\\.]', '', text)
    # Remove extra whitespace
    text = ' '.join(text.split())
    return text.strip()

def extract_after_second_work_notes(text):
    parts = text.split("(Work notes)\n", 2)
    res = parts[2] if len(parts) > 2 else text
    return res

def analyze_top_incidents():
    # Read the CSV file
    df = pd.read_csv('incidents_servicedesk_large.csv', encoding='latin-1')
    
    # Prepare Configuration Item column
    df['Configuration item'] = df['Configuration item'].fillna('Unknown')
    df['Configuration item'] = df['Configuration item'].str.replace(r'[^\w\s]', '')

    # Filter for specific item as needed
    # df = df[df['Configuration item'] == 'Chrome  Browser']
    total_records = len(df)

    # Get and sort top 100 Configuration Items
    top_100_config_items = df['Configuration item'].value_counts().head(100)
    top_100_percentages = (df['Configuration item'].value_counts().head(100) / total_records * 100)
    print("\nTop 100 Configuration Items by Frequency:")
    print("========================================")
    for item, count in top_100_config_items.items():
        percentage = top_100_percentages[item]
        print(f"{item:<60} Count: {count:>5} ({percentage:.1f}% of total)")


    # Get top 30 Configuration Items by frequency
    top_30_config_items = df['Configuration item'].value_counts().head(30)
    top_30_percentages = (df['Configuration item'].value_counts().head(30) / total_records * 100)


    # Creat dataframe for training data with top 30 configuration items
    csv_results = []


    print("\nTop 30 Configuration Items Analysis:")
    print("====================================")
    
    # For each top configuration item, analyze short descriptions
    for config_item, count in top_30_config_items.items():
        # Get subset of data for this configuration item
        config_df = df[df['Configuration item'] == config_item].copy()
        
        # Clean and prepare Short description
        config_df.loc[:, 'Short description'] = config_df['Short description'].fillna('No description')
        config_df.loc[:, 'Short description'] = config_df['Short description'].str.lower()
        config_df.loc[:, 'Short description'] = config_df['Short description'].str.replace(r'[^\w\s]', '')

        # Create TF-IDF vectors for short descriptions
        desc_vectorizer = TfidfVectorizer(max_features=500, stop_words='english', min_df=2)
        # print(config_df['Short description'], "length", len(config_df))
        
        if len(config_df) > 5:  # Only cluster if we have enough samples
            desc_tfidf = desc_vectorizer.fit_transform(config_df['Short description'])
            
            # Perform clustering on short descriptions
            n_clusters = min(5, len(config_df))
            desc_kmeans = KMeans(n_clusters=n_clusters, random_state=42)
            config_df.loc[:, 'desc_cluster'] = desc_kmeans.fit_predict(desc_tfidf)
            
            for cluster_id in range(n_clusters):
                cluster_docs = config_df[config_df['desc_cluster'] == cluster_id]['Short description'].tolist()
                cluster_size = len(cluster_docs)
                
                # Preprocess all descriptions
                processed_docs = [preprocess_description(doc) for doc in cluster_docs]
                
                # Create TF-IDF vectors for similarity comparison
                similarity_vectorizer = TfidfVectorizer(stop_words='english')
                tfidf_matrix = similarity_vectorizer.fit_transform(processed_docs)
                
                # Calculate similarity scores
                similarity_matrix = cosine_similarity(tfidf_matrix)
                
                # Find description with highest average similarity to others
                avg_similarities = similarity_matrix.mean(axis=1)
                representative_idx = avg_similarities.argmax()
                
                # Use original (unprocessed) description as label
                representative_description = cluster_docs[representative_idx]
                
                # Print the cluster description
                print(f"\nCluster {cluster_id + 1} Short Description: {representative_description[:100]}")
                print(f"Size: {cluster_size} records")
                
                # Get work notes for this cluster's records
                cluster_records = config_df[config_df['desc_cluster'] == cluster_id]
                cluster_notes = cluster_records['Work notes'].tolist()
                
                if len(cluster_notes) > 0:
                    print("Top 5 associated work notes:")
                    # Process and analyze work notes for this cluster
                    processed_notes = [preprocess_notes(note) for note in cluster_notes]
                    notes_vectorizer = TfidfVectorizer(stop_words='english')
                    notes_tfidf = notes_vectorizer.fit_transform(processed_notes)
                    notes_similarity = cosine_similarity(notes_tfidf)
                    
                    # Find top 5 most representative work notes
                    avg_note_similarities = notes_similarity.mean(axis=1)
                    top_5_indices = avg_note_similarities.argsort()[-5:][::-1]
                    
                    for idx in top_5_indices:
                        similarity_score = avg_note_similarities[idx]
                        print(f"    - {processed_notes[idx][:200]} (Similarity: {similarity_score:.2f})")
                        # Save cluster results to CSV
                        csv_results.append({
                            'config_item': config_item,
                            'short_description': representative_description,
                            'work_note': processed_notes[idx]
                        })

                    print("-" * 80)

        else:
            print(f"Not enough data to perform clustering for {config_item}. Skipping...")

        # Combine all cluster results
        results_df = pd.DataFrame(csv_results)
        results_df.to_csv('helpdesk_incident_train_data.csv', index=False)
        
    return top_30_config_items

if __name__ == "__main__":
    top_incidents = analyze_top_incidents()