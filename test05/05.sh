# Script generates random password, opens port 8765 and listens for connections
# On incoming connection script responds with generated password
# When client closes the connection, script waits for 10 seconds and repeats

# Check if nc, md5sum, sha1sum utils exist
if ! which nc
then
    echo "nc not found"
    exit 1
fi

if ! which md5sum
then
    echo "md5sum not found"
    exit 1
fi

if ! which sha1sum
then
    echo "sha1sum not found"
    exit 1
fi

# Save initial message to respond
echo "Access denied" > /tmp/msg

while true
do
# Generate password, set it to user blooper and save in msg file
    PW="$(echo $((RANDOM % 7923456982376 * $((RANDOM % 7923456982376 * $((RANDOM % 7923456982376))))))$(date +%Y%m%d%HH%MM) | md5sum | sha1sum | cut -d " " -f 1)"
    echo "blooper:$PW" | chpasswd
    echo $PW > /tmp/msg
# Listen to 8765 and respond with content of msg file
    { echo -ne "HTTP/1.0 200 OK\r\n\r\n"; cat /tmp/msg; } | nc -l -p 8765
# Wait 10 seconds and repeat
    sleep 10
done


# What can be changed depends on what is expected exactly
# I.e. now no other client can receive password unless current client disconnects and 10 seconds pass
# So we could send 'Content-length' header to ask client to disconnect right after password received
# Or set a timeout via '-w' flag
# But it might have been done intentionally, who knows
#
# Also sending passwords via plain http might look like an issue
# Maybe something like openssl instead of nc could be used
# But if this script is used in internal, trusted network, no problem there
