program main

implicit none
    integer :: istat, i, iunit, n_rows
    real(kind=8), dimension (:,:), allocatable :: data_array
    real(kind=8), dimension (:), allocatable :: time_input, water_level
    real(kind=8) :: tmp, time, y
    character(len=255) :: data_dir

    iunit = 10
    call getenv("DATA_DIR", data_dir)
    open(iunit, file=trim(adjustl(data_dir))//'/WaterLevel_low.bc', status='OLD', iostat=istat)

    rewind(iunit)
    n_rows = 0
    do
        read(iunit, *, iostat=istat) tmp
        if (is_iostat_end(istat)) exit
        n_rows = n_rows + 1
    end do

    allocate(data_array(n_rows, 2))
    allocate(time_input(n_rows))
    allocate(water_level(n_rows))

    rewind(iunit)
    do i= 1, n_rows
        read(iunit, *, iostat=istat) data_array(i,:)
    end do

    close(unit=iunit, iostat=istat)

    time_input(:) = data_array(:,1)
    water_level(:) = data_array(:,2)

    deallocate(data_array)

    time = (time_input(1) + time_input(2)) * 0.5

    do i = 2, n_rows
        if ((time > time_input(i-1)) .and. (time < time_input(i))) then
            call parabola_val2(n_rows, time_input, water_level, i, time, y)
            exit
        end if
    end do

    write(*,*) time, y, water_level(1), water_level(2)

    deallocate(time_input)
    deallocate(water_level)

end program main

subroutine parabola_val2(ndata, tdata, ydata, left, tval, yval)

!*****************************************************************************80
!
!! PARABOLA_VAL2 evaluates a parabolic interpolant through tabular data.
!
!  Discussion:
!
!    This routine is a utility routine used by OVERHAUSER_SPLINE_VAL.
!    It constructs the parabolic interpolant through the data in
!    3 consecutive entries of a table and evaluates this interpolant
!    at a given abscissa value.
!
!  Licensing:
!
!    This code is distributed under the GNU LGPL license.
!
!  Modified:
!
!    26 January 2004
!
!  Author:
!
!    John Burkardt
!
!  Parameters:
!
!    Input, integer ( kind = 4 ) NDATA, the number of data points.
!    NDATA must be at least 3.
!
!    Input, real ( kind = 8 ) TDATA(NDATA), the abscissas of the data
!    points.  The values in TDATA must be in strictly ascending order.
!
!    Input, real ( kind = 8 ) YDATA(DIM_NUM,NDATA), the data points
!    corresponding to the abscissas.
!
!    Input, integer ( kind = 4 ) LEFT, the location of the first of the three
!    consecutive data points through which the parabolic interpolant
!    must pass.  1 <= LEFT <= NDATA - 2.
!
!    Input, real ( kind = 8 ) TVAL, the value of T at which the parabolic
!    interpolant is to be evaluated.  Normally, TDATA(1) <= TVAL <= T(NDATA),
!    and the data will be interpolated.  For TVAL outside this range,
!    extrapolation will be used.
!
!    Output, real ( kind = 8 ) YVAL(DIM_NUM), the value of the parabolic
!    interpolant at TVAL.
!
  implicit none

  integer ( kind = 4 ) ndata

  real ( kind = 8 ) dif1
  real ( kind = 8 ) dif2
  integer ( kind = 4 ) i
  integer ( kind = 4 ) left
  real ( kind = 8 ) t1
  real ( kind = 8 ) t2
  real ( kind = 8 ) t3
  real ( kind = 8 ) tval
  real ( kind = 8 ) tdata(ndata)
  real ( kind = 8 ) ydata(ndata)
  real ( kind = 8 ) y1
  real ( kind = 8 ) y2
  real ( kind = 8 ) y3
  real ( kind = 8 ) yval
!
!  Check.
!
  if ( left < 1 ) then
    write ( *, '(a)' ) ' '
    write ( *, '(a)' ) 'PARABOLA_VAL2 - Fatal error!'
    write ( *, '(a)' ) '  LEFT < 1.'
    write ( *, '(a,i8)' ) '  LEFT = ', left
    stop 1
  end if

  if ( ndata-2 < left ) then
    write ( *, '(a)' ) ' '
    write ( *, '(a)' ) 'PARABOLA_VAL2 - Fatal error!'
    write ( *, '(a)' ) '  NDATA-2 < LEFT.'
    write ( *, '(a,i8)' ) '  NDATA = ', ndata
    write ( *, '(a,i8)' ) '  LEFT =  ', left
    stop 1
  end if
!
!  Copy out the three abscissas.
!
  t1 = tdata(left)
  t2 = tdata(left+1)
  t3 = tdata(left+2)

  if ( t2 <= t1 .or. t3 <= t2 ) then
    write ( *, '(a)' ) ' '
    write ( *, '(a)' ) 'PARABOLA_VAL2 - Fatal error!'
    write ( *, '(a)' ) '  T2 <= T1 or T3 <= T2.'
    stop 1
  end if
!
!  Construct and evaluate a parabolic interpolant for the data
!  in each dimension.
!

  y1 = ydata(left)
  y2 = ydata(left+1)
  y3 = ydata(left+2)

  dif1 = ( y2 - y1 ) / ( t2 - t1 )
  dif2 = ( ( y3 - y1 ) / ( t3 - t1 ) &
       - ( y2 - y1 ) / ( t2 - t1 ) ) / ( t3 - t2 )
  yval = y1 + ( tval - t1 ) * ( dif1 + ( tval - t2 ) * dif2 )

  return
end
