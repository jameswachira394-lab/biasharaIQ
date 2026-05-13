#!/usr/bin/env python3
"""
M-Pesa Configuration Setup Wizard
Helps you configure and validate M-Pesa credentials
"""

import os
import sys
from pathlib import Path


def print_header(text):
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60)


def print_step(step_num, text):
    print(f"\n[Step {step_num}] {text}")


def print_info(text):
    print(f"  ℹ  {text}")


def print_warning(text):
    print(f"  ⚠  {text}")


def print_success(text):
    print(f"  ✓  {text}")


def print_error(text):
    print(f"  ✗  {text}")


def get_input_masked(prompt):
    """Get input but mask it for sensitive data"""
    from getpass import getpass
    return getpass(prompt + " (hidden): ")


def get_input_visible(prompt):
    """Get visible input"""
    return input(prompt + ": ").strip()


def main():
    print_header("M-Pesa Daraja API Configuration Wizard")
    
    print_info("This tool will help you configure M-Pesa payment integration")
    print_info("Make sure you have registered at: https://developer.safaricom.co.ke/")
    
    # Detect backend directory
    backend_dir = Path(__file__).parent / "backend"
    env_file = backend_dir / ".env"
    
    if not backend_dir.exists():
        print_error(f"Backend directory not found at {backend_dir}")
        sys.exit(1)
    
    print_info(f"Backend directory: {backend_dir}")
    print_info(f"Will save configuration to: {env_file}")
    
    # Get environment
    print_step(1, "Select M-Pesa Environment")
    print_info("Choose 'sandbox' for testing or 'production' for live payments")
    environment = input("Environment [sandbox/production] (default: sandbox): ").strip().lower() or "sandbox"
    
    if environment not in ["sandbox", "production"]:
        print_error(f"Invalid environment: {environment}")
        sys.exit(1)
    
    print_success(f"Environment: {environment}")
    
    # Get credentials
    print_step(2, "Enter M-Pesa Credentials")
    
    if environment == "sandbox":
        print_info("For sandbox testing, you'll need test credentials from Safaricom Daraja")
        print_info("Get your credentials at: https://developer.safaricom.co.ke/")
    else:
        print_warning("For production, use your Safaricom business credentials")
    
    consumer_key = get_input_visible("\nConsumer Key (from Safaricom Developer)")
    if not consumer_key:
        print_error("Consumer Key is required")
        sys.exit(1)
    
    consumer_secret = get_input_masked("\nConsumer Secret")
    if not consumer_secret:
        print_error("Consumer Secret is required")
        sys.exit(1)
    
    # Shortcode and Passkey
    print_step(3, "Enter M-Pesa Shortcode and Passkey")
    
    if environment == "sandbox":
        default_shortcode = "174379"
        default_passkey = "bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919"
        print_info(f"Default sandbox shortcode: {default_shortcode}")
        shortcode_input = input(f"Shortcode [default: {default_shortcode}]: ").strip()
        shortcode = shortcode_input or default_shortcode
        
        passkey_input = get_input_visible(f"Passkey [default: {default_passkey[:20]}...]")
        passkey = passkey_input or default_passkey
    else:
        shortcode = get_input_visible("\nShortcode (from Safaricom)")
        if not shortcode:
            print_error("Shortcode is required")
            sys.exit(1)
        
        passkey = get_input_masked("\nPasskey")
        if not passkey:
            print_error("Passkey is required")
            sys.exit(1)
    
    print_success(f"Shortcode: {shortcode}")
    print_success(f"Passkey: {'*' * 20}...")
    
    # Callback URL
    print_step(4, "Enter M-Pesa Callback URL")
    
    if environment == "sandbox":
        print_info("For local testing, you can use: http://localhost:8000/payments/callback")
        default_callback = "http://localhost:8000/payments/callback"
    else:
        print_info("This must be your production API domain")
        print_info("Example: https://api.biashara-iq.com/payments/callback")
        print_warning("⚠  Must be HTTPS for production!")
        default_callback = ""
    
    callback_input = get_input_visible(
        f"\nCallback URL" + (f" [default: {default_callback}]" if default_callback else "")
    )
    callback_url = callback_input or default_callback
    
    if not callback_url:
        print_error("Callback URL is required")
        sys.exit(1)
    
    print_success(f"Callback URL: {callback_url}")
    
    # Summary and confirmation
    print_step(5, "Configuration Summary")
    print("\nConfiguration to be saved:")
    print(f"  MPESA_ENVIRONMENT={environment}")
    print(f"  MPESA_CONSUMER_KEY={consumer_key}")
    print(f"  MPESA_CONSUMER_SECRET={'*' * 20}...")
    print(f"  MPESA_SHORTCODE={shortcode}")
    print(f"  MPESA_PASSKEY={'*' * 20}...")
    print(f"  MPESA_CALLBACK_URL={callback_url}")
    
    confirm = input("\nProceed with saving configuration? [y/N]: ").strip().lower()
    if confirm != 'y':
        print_warning("Configuration not saved")
        sys.exit(0)
    
    # Save to .env file
    print_step(6, "Saving Configuration")
    
    try:
        # Read existing .env if it exists
        existing_content = ""
        if env_file.exists():
            with open(env_file, 'r') as f:
                existing_content = f.read()
        
        # Update or add M-Pesa configuration
        new_env_lines = []
        mpesa_keys = {
            'MPESA_ENVIRONMENT', 'MPESA_CONSUMER_KEY', 'MPESA_CONSUMER_SECRET',
            'MPESA_SHORTCODE', 'MPESA_PASSKEY', 'MPESA_CALLBACK_URL'
        }
        
        # Parse existing lines
        for line in existing_content.split('\n'):
            if line.strip() and not any(line.startswith(key) for key in mpesa_keys):
                new_env_lines.append(line)
        
        # Add M-Pesa configuration
        new_env_lines.extend([
            "",
            "# M-Pesa Daraja API Configuration",
            f"MPESA_ENVIRONMENT={environment}",
            f"MPESA_CONSUMER_KEY={consumer_key}",
            f"MPESA_CONSUMER_SECRET={consumer_secret}",
            f"MPESA_SHORTCODE={shortcode}",
            f"MPESA_PASSKEY={passkey}",
            f"MPESA_CALLBACK_URL={callback_url}",
            ""
        ])
        
        # Write back to file
        with open(env_file, 'w') as f:
            f.write('\n'.join(new_env_lines))
        
        print_success(f"Configuration saved to {env_file}")
        
    except Exception as e:
        print_error(f"Failed to save configuration: {str(e)}")
        sys.exit(1)
    
    # Next steps
    print_step(7, "Next Steps")
    print_info("1. Restart the backend server:")
    print("   python main.py")
    print_info("2. Test the payment endpoint:")
    print("   python test_mpesa_integration.py")
    print_info("3. Check logs for any errors:")
    print("   tail -f backend.log")
    
    print_header("Setup Complete!")
    print_info("M-Pesa integration is now configured")
    print_info("Try initiating a payment from the frontend")
    print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nSetup cancelled by user")
        sys.exit(0)
    except Exception as e:
        print_error(f"Unexpected error: {str(e)}")
        sys.exit(1)
