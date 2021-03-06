#!/bin/bash

if [ "$REQUEST_METHOD" = "POST" ]; then
  POST=$(</dev/stdin)
  # Start / Stop container
  if [[ $POST =~ ^toggleService=(.*)$ ]]; then
    service="${BASH_REMATCH[1]}"
    if [[ "$(docker ps)" =~ $service ]]; then
      docker stop $service > /dev/null
    else
      docker start $service > /dev/null
    fi
  fi
  # Duplication / Fork
  if [[ $POST =~ ^duplicate=(.*)\&name=(.*)$ ]]; then
    serviceId="${BASH_REMATCH[1]}"
    serviceName="${BASH_REMATCH[2]}""-duplicated"
    if [[ "$(docker ps)" =~ $serviceId ]]; then
      stopped=true
      docker stop $serviceId > /dev/null
    fi
    docker commit $serviceId $serviceName
    docker run --restart=always -d $serviceName
    if [ "$stopped" = true ] ; then
      docker start $serviceId
    fi
  fi
  # Suppression
  if [[ $POST =~ ^delete=(.*)$ ]]; then
    service="${BASH_REMATCH[1]}"
    if [[ "$(docker ps)" =~ $service ]]; then
      docker stop $service > /dev/null
    fi
    docker rm $service
  fi
  # Rename container
  if [[ $POST =~ ^newName=(.*)\&oldName=(.*)$ ]]; then
    newName="${BASH_REMATCH[1]}"
    oldName="${BASH_REMATCH[2]}"
    docker rename "$oldName" "$newName"
  fi
  # Install from Docker Hub
  if [[ $POST =~ ^installDockerhubApp=(.*)\&dockerPort=(.*)$ ]]; then
    app="${BASH_REMATCH[1]}"
    port="${BASH_REMATCH[2]}"
    (docker pull $app > /dev/null; docker run --restart=always -p $port:80 -d $app > /dev/null )&
    $app"\n" >> ../dockerfile/image.dat
  fi
  # add wordpress
  if [[ $POST =~ ^wordpress=install\&wordpressName=(.*)\&wordpressPort=(.*)\&mysqlPass=(.*)$ ]]; then
    wpName="${BASH_REMATCH[1]}"
    mysqlName="mysql-"$wpName
    wpPort="${BASH_REMATCH[2]}"
    mysqlPass="${BASH_REMATCH[3]}"
    docker run --restart=always --name $mysqlName -e MYSQL_ROOT_PASSWORD=$mysqlPass -d mysql:latest > /dev/null
    docker run --restart=always --name $wpName --link $mysqlName:mysql -p $wpPort:80 -d wordpress > /dev/null
  fi
  # add djangocms
  if [[ $POST =~ ^djangocms=install\&djangocmsName=(.*)\&djangocmsPort=(.*)$ ]]; then
    djcmsName="${BASH_REMATCH[1]}"
    djcmsPort="${BASH_REMATCH[2]}"
    docker run --restart=always --name $djcmsName -p $wpPort:8000 -d bluszcz/djangocms > /dev/null
  fi
  # change container port
  if [[ $POST =~ ^newPort=(.*)\&serviceId=(.*)\&imageName=(.*)$ ]]; then
    newPort="${BASH_REMATCH[1]/'%3A'/:}"
    serviceId="${BASH_REMATCH[2]}"
    imageName="${BASH_REMATCH[3]}"
    if [[ "$(docker ps)" =~ $serviceId ]]; then
      docker stop $serviceId  > /dev/null
    fi
    
    # on retire le tag
    if [[ $imageName =~ ^(.*)%3A(.*)$ ]]; then
      imageName="${BASH_REMATCH[1]}"
    fi
    # on regarde s'il s'agit d'une image mère
    if [[ "$(cat ../dockerfile/image.dat)" =~ $imageName ]]; then
      i=1
      while [[ "$(docker images)" =~ $imageName"-"$i ]]; do
        i=$i+1
      done;
      imageName=$imageName"-"$i
    fi
    
    docker commit $serviceId $imageName > /dev/null
    docker run --restart=always -p $newPort -td $imageName > /dev/null
    docker rm $serviceId > /dev/null
  fi
fi

echo "Content-type: text/html"
echo ""

echo '<html>'
echo '<head>'
echo '<meta http-equiv="Content-Type" content="text/html; charset=UTF-8">'
echo '<title>Adminsys</title>'
echo '<link rel="stylesheet" type="text/css" href="../style/style.css">'
echo '<link rel="stylesheet" type="text/css" href="../style/togglebutton.css">'
echo '</head>'
echo '<body>'
echo '  <div id="header">'
echo '  </div>'
echo '  <div id="content">'
#echo '    <div id="userinfo">'
#echo '      <p>DjangoCMS Login : admin / Pass : djangocms</p>'
#echo '    </div>'
echo "    <h1> Interface d'administration </h1>"
echo "    <h2> Services en cours d'éxecution </h2>"
echo '    <div id="services">'
python ../format/containers.py "$(docker ps -a)"
echo '      <div id="tools">'
echo '        <input type="button" onclick="location.replace(location.href)" value="Reload" id="reloadButton">'
echo '      </div>'
echo '    </div>'
echo "    <h2> Installer de nouveaux services </h2>"
echo '    <div class="installer" id="customInstaller">'
echo '      <form method="post" action="docker_handler.cgi">'
echo '        <input type="checkbox" name="wordpress" value="install" id="wordpress">'
echo '        <label for="wordpress"><img src="https://s.w.org/favicon.ico" width="15" height="15">Wordpress</label>'
echo '        <div class="installerMenu" id="wordpressInstaller">'
echo '          <table>'
echo '            <tr>'
echo '              <td><label>Nom du container</label></td>'
echo '              <td><input type="text" name="wordpressName" value="wordpress" ><td>'
echo '            </tr>'
echo '            <tr>'
echo '              <td><label>Port</label></td>'
echo '              <td><input type="text" name="wordpressPort" value="8080" ></td>'
echo '            </tr>'
echo '            <tr>'
echo '              <td><label>Mot de passe mysql</label></td>'
echo '              <td><input type="password" name="mysqlPass" value="root" ></td>'
echo '            </tr>'
echo '          </table>'
echo '        </div>'
echo '        <input type="button" onclick="this.form.submit();" value="Create" style="display:block; margin:20 0 0 10px;">'
echo '      </form>'
echo '    </div>'

echo '    <div class="installer" id="customInstaller">'
echo '      <form method="post" action="docker_handler.cgi">'
echo '        <input type="checkbox" name="djangocms" value="install" id="djangocms">'
echo '        <label for="djangocms"><img src="http://www.django-cms.org/static/favicon.ico" width="15" height="15">djangocms</label>'
echo '        <div class="installerMenu" id="djangocmsInstaller">'
echo '          <table>'
echo '            <tr>'
echo '              <td><label>Nom du container</label></td>'
echo '              <td><input type="text" name="djangocmsName" value="djangocms" ><td>'
echo '            </tr>'
echo '            <tr>'
echo '              <td><label>Port</label></td>'
echo '              <td><input type="text" name="djangocmsPort" value="8080" ></td>'
echo '            </tr>'
echo '            <tr>'
echo '              <td><label>Login : admin / Pass : djangocms</label></td>'
echo '            </tr>'
echo '          </table>'
echo '        </div>'
echo '        <input type="button" onclick="this.form.submit();" value="Create" style="display:block; margin:20 0 0 10px;">'
echo '      </form>'
echo '    </div>'


echo '    <div class="installer" id="dockerhubInstaller">'
echo '      <form method="post" action="docker_handler.cgi">'
echo '         Docker name (from DockerHub): <input type="text" name="installDockerhubApp"><br>'
echo '         Docker port : <input type="text" name="dockerPort"><br>'
echo '      <input type="submit"value="Create" style="display:block; margin:20 0 0 10px;">'
echo '      </form>'
echo '    </div>'

echo '  </div>'
echo '</body>'
echo '</html>'

exit 0
