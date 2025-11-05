# New-LocalUser -Name "User1" -Password (ConvertTo-SecureString -AsPlainText "Password1" -Force) -FullName "User One" -Description "First User Account"
# Add-LocalGroupMember -Group "Administrators" -Member "User1"  # Optional, adds User1 to the Administrators group

# New-LocalUser -Name "User2" -Password (ConvertTo-SecureString -AsPlainText "Password2" -Force) -FullName "User Two" -Description "Second User Account"
# Add-LocalGroupMember -Group "Administrators" -Member "User2"  # Optional, adds User2 to the Administrators group

# Add User2 to any specific group if needed
