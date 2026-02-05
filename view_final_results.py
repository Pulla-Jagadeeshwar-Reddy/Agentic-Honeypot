#!/usr/bin/env python3
"""
Final Results Viewer
View all final results that were sent to GUVI evaluation endpoint
"""

import json
import os
from datetime import datetime
from pathlib import Path


def list_all_results():
    """List all saved final results"""
    results_dir = Path("results")
    
    if not results_dir.exists():
        print("No results directory found. Run some test scenarios first.")
        return
    
    result_files = list(results_dir.glob("final_result_*.json"))
    
    if not result_files:
        print("No final results saved yet.")
        return
    
    print("\n" + "="*80)
    print(f"FINAL RESULTS SENT TO GUVI ({len(result_files)} total)")
    print("="*80 + "\n")
    
    for i, file_path in enumerate(sorted(result_files), 1):
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            print(f"{i}. Session: {data.get('sessionId', 'Unknown')}")
            print(f"   File: {file_path.name}")
            print(f"   Scam Detected: {data.get('scamDetected', False)}")
            print(f"   Messages: {data.get('totalMessagesExchanged', 0)}")
            
            intel = data.get('extractedIntelligence', {})
            print(f"   Intelligence: {len(intel.get('upiIds', []))} UPIs, "
                  f"{len(intel.get('phoneNumbers', []))} phones, "
                  f"{len(intel.get('phishingLinks', []))} links")
            print()
            
        except Exception as e:
            print(f"Error reading {file_path}: {e}\n")


def view_result(file_or_session):
    """View a specific result in detail"""
    results_dir = Path("results")
    
    # Try to find the file
    if file_or_session.endswith('.json'):
        file_path = results_dir / file_or_session
    else:
        # Search by session ID
        matching = list(results_dir.glob(f"final_result_{file_or_session}_*.json"))
        if not matching:
            print(f"No results found for session: {file_or_session}")
            return
        file_path = matching[0]
    
    if not file_path.exists():
        print(f"File not found: {file_path}")
        return
    
    with open(file_path, 'r') as f:
        data = json.load(f)
    
    print("\n" + "="*80)
    print("FINAL RESULT SENT TO GUVI")
    print("="*80 + "\n")
    
    print(f"Session ID: {data['sessionId']}")
    print(f"Scam Detected: {data['scamDetected']}")
    print(f"Total Messages: {data['totalMessagesExchanged']}")
    print(f"\nAgent Notes:\n{data['agentNotes']}\n")
    
    print("-" * 80)
    print("EXTRACTED INTELLIGENCE")
    print("-" * 80)
    
    intel = data['extractedIntelligence']
    
    if intel.get('upiIds'):
        print(f"\n💳 UPI IDs ({len(intel['upiIds'])}):")
        for upi in intel['upiIds']:
            print(f"  • {upi}")
    
    if intel.get('bankAccounts'):
        print(f"\n🏦 Bank Accounts ({len(intel['bankAccounts'])}):")
        for acc in intel['bankAccounts']:
            print(f"  • {acc}")
    
    if intel.get('phoneNumbers'):
        print(f"\n📞 Phone Numbers ({len(intel['phoneNumbers'])}):")
        for phone in intel['phoneNumbers']:
            print(f"  • {phone}")
    
    if intel.get('phishingLinks'):
        print(f"\n🔗 Phishing Links ({len(intel['phishingLinks'])}):")
        for link in intel['phishingLinks']:
            print(f"  • {link}")
    
    if intel.get('suspiciousKeywords'):
        print(f"\n🚩 Suspicious Keywords ({len(intel['suspiciousKeywords'])}):")
        keywords = ', '.join(intel['suspiciousKeywords'][:20])
        if len(intel['suspiciousKeywords']) > 20:
            keywords += f" ... (+{len(intel['suspiciousKeywords']) - 20} more)"
        print(f"  {keywords}")
    
    print("\n" + "="*80)
    print(f"Saved in: {file_path}")
    print("="*80 + "\n")


def summarize_all():
    """Summarize all results"""
    results_dir = Path("results")
    
    if not results_dir.exists():
        print("No results directory found.")
        return
    
    result_files = list(results_dir.glob("final_result_*.json"))
    
    if not result_files:
        print("No results to summarize.")
        return
    
    total_sessions = len(result_files)
    total_messages = 0
    total_upis = 0
    total_phones = 0
    total_links = 0
    total_banks = 0
    
    all_upis = set()
    all_phones = set()
    all_links = set()
    
    for file_path in result_files:
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            total_messages += data.get('totalMessagesExchanged', 0)
            intel = data.get('extractedIntelligence', {})
            
            upis = intel.get('upiIds', [])
            phones = intel.get('phoneNumbers', [])
            links = intel.get('phishingLinks', [])
            banks = intel.get('bankAccounts', [])
            
            total_upis += len(upis)
            total_phones += len(phones)
            total_links += len(links)
            total_banks += len(banks)
            
            all_upis.update(upis)
            all_phones.update(phones)
            all_links.update(links)
            
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
    
    print("\n" + "="*80)
    print("INTELLIGENCE SUMMARY - ALL SESSIONS")
    print("="*80 + "\n")
    
    print(f"Total Sessions: {total_sessions}")
    print(f"Total Messages Exchanged: {total_messages}")
    print(f"Average Messages per Session: {total_messages / total_sessions:.1f}")
    print()
    
    print("Total Intelligence Extracted:")
    print(f"  • UPI IDs: {total_upis} ({len(all_upis)} unique)")
    print(f"  • Phone Numbers: {total_phones} ({len(all_phones)} unique)")
    print(f"  • Phishing Links: {total_links} ({len(all_links)} unique)")
    print(f"  • Bank Accounts: {total_banks}")
    print()
    
    if all_upis:
        print("Unique UPI IDs Found:")
        for upi in sorted(all_upis):
            print(f"  • {upi}")
        print()
    
    if all_phones:
        print("Unique Phone Numbers Found:")
        for phone in sorted(all_phones):
            print(f"  • {phone}")
        print()
    
    if all_links:
        print("Unique Phishing Links Found:")
        for link in sorted(all_links):
            print(f"  • {link}")
        print()


def export_csv():
    """Export results to CSV format"""
    results_dir = Path("results")
    
    if not results_dir.exists():
        print("No results directory found.")
        return
    
    result_files = list(results_dir.glob("final_result_*.json"))
    
    if not result_files:
        print("No results to export.")
        return
    
    csv_file = f"intelligence_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    
    with open(csv_file, 'w') as f:
        # Header
        f.write("Session ID,Scam Detected,Messages,UPIs,Phones,Links,Banks\n")
        
        for file_path in sorted(result_files):
            try:
                with open(file_path, 'r') as rf:
                    data = json.load(rf)
                
                intel = data.get('extractedIntelligence', {})
                
                f.write(f"{data['sessionId']},")
                f.write(f"{data['scamDetected']},")
                f.write(f"{data['totalMessagesExchanged']},")
                f.write(f"{len(intel.get('upiIds', []))},")
                f.write(f"{len(intel.get('phoneNumbers', []))},")
                f.write(f"{len(intel.get('phishingLinks', []))},")
                f.write(f"{len(intel.get('bankAccounts', []))}\n")
                
            except Exception as e:
                print(f"Error processing {file_path}: {e}")
    
    print(f"✓ Exported to {csv_file}")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("""
Usage:
  python view_final_results.py list              # List all results
  python view_final_results.py view <session-id> # View specific result
  python view_final_results.py summary           # Summary of all results
  python view_final_results.py export            # Export to CSV

Examples:
  python view_final_results.py list
  python view_final_results.py view bank-fraud-001
  python view_final_results.py summary
        """)
        sys.exit(0)
    
    command = sys.argv[1]
    
    if command == "list":
        list_all_results()
    
    elif command == "view" and len(sys.argv) > 2:
        view_result(sys.argv[2])
    
    elif command == "summary":
        summarize_all()
    
    elif command == "export":
        export_csv()
    
    else:
        print("Invalid command. Use: list, view, summary, or export")